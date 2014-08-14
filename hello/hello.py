import os
from flask import Flask
import xml.etree.ElementTree as ET
import logging

app = Flask(__name__)

@app.route('/')
def hello():
    logging.info('hello')
    return 'nothing here'

@app.route('/xmlrpc.php')
def xmlrpc():
    logging.info('xmlrpc')
    return 'test'

