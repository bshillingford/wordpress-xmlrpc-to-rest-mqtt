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
        result = (['metaWeblog.newPost', 'metaWeblog.getRecentPosts'],)
    elif func == 'metaWeblog.getRecentPosts':
        #result = ([],)
        result = ([{'categories': ['Uncategorized'],
            'custom_fields': [],
            'dateCreated': xmlrpclib.DateTime('20140726T10:28:55'),
            'date_created_gmt': xmlrpclib.DateTime('20140726T10:28:55'),
            'date_modified': xmlrpclib.DateTime('20140727T00:04:26'),
            'date_modified_gmt': xmlrpclib.DateTime('20140727T00:04:26'),
            'description': 'short post with no title **bold** *italics...*',
            'link': 'http://96.48.73.164/2014/07/26/posts/32',
            'mt_allow_comments': 1,
            'mt_allow_pings': 1,
            'mt_excerpt': '',
            'mt_keywords': '',
            'mt_text_more': '',
            'permaLink': 'http://96.48.73.164/2014/07/26/posts/32',
            'post_status': 'publish',
            'postid': '32',
            'sticky': False,
            'title': 'short post with no title **bold** *italics *',
            'userid': '3',
            'wp_author_display_name': 'Brendan',
            'wp_author_id': '3',
            'wp_more_text': '',
            'wp_password': '',
            'wp_post_format': 'chat',
            'wp_post_thumbnail': '',
            'wp_slug': '32'}],)
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

    returned_xml = xmlrpclib.dumps(result, methodresponse=True)

    logging.info('RPC:' + request.data + "\n\n" + returned_xml)

    return returned_xml

