import os
from flask import Flask
from flask import request
from .utils import returns_xml, parse_bool
import xmlrpclib
import paho.mqtt.publish as publish
import traceback
import sys
import urlparse
import re
import requests

app = Flask(__name__)
logging = app.logger
#app.debug = True

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
    elif func == 'metaWeblog.newPost':
        title = args[3]['title']
        body = args[3]['description']
        result = new_post_helper(title, body)
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

def new_post_helper(title, body):
    try:
        title_parsed = re.match(r'(?P<method>GET|POST|PUT|MQTT-PUB) (?P<url>\S+)', title, re.I)
        if not title_parsed:
            raise ValueError("invalid title, check method (should be one of GET/POST/PUT/MQTT-PUB) and URI")
        method, url = title_parsed.groups()
        method = method.upper()

        if method == "MQTT-PUB":
            # Example format for URL: (topic a/b/c/d)
            #     mqtt://iot.eclipse.org/a/b/c/d?qos=2&retain=false
            # Body of message is payload.

            parsed = urlparse.urlparse(url)
            info = dict(urlparse.parse_qsl(parsed.query))
            info['port'] = parsed.port or 1883
            info['hostname'] = parsed.hostname
            info['topic'] = parsed.path[1:]  # omit first slash
            info['payload'] = body
            info['retain'] = parse_bool(info.get('retain', 'False'))
            info['qos'] = int(info.get('qos', 0))

            publish.single(**info)

            summary = 'MQTT-PUB: host={}, topic={}, payload={}, {}'.format(info['hostname'], info['topic'], body, info)

        else:
            # handle HTTP request
            response = requests.request(method, url, data=body if method != "GET" else None)

            summary = ('{status_code} {reason} ({request.method} request to {url}). Response content:\n'
                       '{content}'
                       .format(content=response.text, **response.__dict__))

        logging.info(summary)
        return (summary,)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return e

