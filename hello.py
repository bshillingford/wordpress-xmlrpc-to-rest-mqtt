import os
from flask import Flask
from flask import request
import xmlrpclib

app = Flask(__name__)
logging = app.logger

@app.route('/')
def hello():
    return 'nothing here'

@app.route('/xmlrpc.php', methods=['POST'])
def xmlrpc():
    # request.data is the whole request
    args, func = xmlrpclib.loads(request.data)

    # can exception, for error, or HTTP status code, also for error
    result = None  

    if func == "mt.supportedMethods":
        # FIXME: doesn't let me return a string, what's the correct syntax for supportedMethods?
        result = (['metaWeblog.getRecentPosts'],)
    elif func == 'metaWeblog.getRecentPosts':
        result = ([],)
    elif func == 'metaWeblog.newPost':
        result = (['resulting post text:\n' + repr(args[2]['member'])],)
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

    return xmlrpclib.dumps(result, methodresponse=True)


