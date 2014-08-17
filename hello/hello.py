import os
from flask import Flask
from flask import request
from .utils import returns_xml, parse_bool
import xmlrpclib
import paho.mqtt.publish as publish
import traceback
import sys
import urlparse

app = Flask(__name__)
logging = app.logger
app.debug = True
logging.setLevel(10)

@app.route('/')
def index():
    return 'nothing here'

@app.route('/wordpress/xmlrpc.php', methods=['POST'])
@returns_xml
def xmlrpc():
    # request.data is the whole request
    args, func = xmlrpclib.loads(request.data)

    # can exception, for error, or HTTP status code, also for error
    result = None  

    if func == "mt.supportedMethods":
        result = (['metaWeblog.newPost', 'metaWeblog.getRecentPosts'],)

    elif func == 'metaWeblog.getRecentPosts':
        result = ([],)

    elif func == 'metaWeblog.newPost':  #  TODO: diagnose error it's giving me... maybe postid
        title = args[3]['title']
        body = args[3]['description']
        try:
            method, url = title.split(' ', 1)
            method = method.upper()
            if method not in ("GET", "POST", "PUT", "MQTT-PUB"):
                raise ValueError("method '{}' is not a valid method or MQTT-PUB".format(method))

            if method == "MQTT-PUB":
                # Example format for URL: (topic a/b/c/d)
                #     mqtt://iot.eclipse.org/a/b/c/d?qos=2&retain=false
                # Body of message is payload.
                print repr(body)
                parsed = urlparse.urlparse(url)
                info = dict(urlparse.parse_qsl(parsed.query))
                info['port'] = parsed.port or 1883
                info['hostname'] = parsed.hostname
                info['topic'] = parsed.path[1:]  # omit first slash
                info['payload'] = body

                if 'retain' in info:
                    info['retain'] = parse_bool(info['retain'])
                for int_param in ('qos', 'port'):
                    if int_param in info:
                        info[int_param] = int(info[int_param])

                if 'hostname' not in info:
                    raise Exception("missing hostname parameter in body")

                publish.single(**info)
                logging.info('MQTT-PUB: host={}, topic={}, payload={}, {}', info['hostname'], info['topic'], body, info)

            else:
                # handle HTTP request
                response = requests.request(method, url)

                summary = ('{status_code} {reason} ({request.method} request to {url}). Response content:\n'
                           '{content}'
                           .format(content=response.text, **response.__dict__))

                logging.info(summary)
                result = (summary, )

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logging.error(str(e))
            raise

    else:
        result = Exception('unsupported function "%s"' % func)

    if isinstance(result, tuple):
        pass  # leave as is
    elif isinstance(result, Exception):
        result = xmlrpclib.Fault(1, str(result))
    elif isinstance(result, int):
        result = xmlrpclib.Fault(result, "HTTP error %d" % result)
    else:
        logging.error('unhandled case')
        result = xmlrpclib.Fault(2, "unhandled case")

    returned_xml = xmlrpclib.dumps(result, methodresponse=True)
    logging.debug('RPC:' + request.data + "\n\n" + returned_xml)
    return returned_xml


