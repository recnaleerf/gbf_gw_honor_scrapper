import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.options

import socket
import uuid
import signal
import logging
import configparser
import os
import json

from scrapper.scheduled_scrapper import scheduledScrapper 

class WSHandler(tornado.websocket.WebSocketHandler):

    config = configparser.ConfigParser()
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, '..', '..', 'conf', 'config.ini')
    config.read(path)

    LOGGER = logging.getLogger(__name__)

    server_address = {}
    clients_address = {}
    clients_portfolio = {}

    def __init__(self, application, request, **kwargs):
        super(WSHandler, self).__init__(application, request, **kwargs)
        self.client_id = str(uuid.uuid4())

    def open(self):
        self.clients_address[self.client_id] = self
        self.write_message(json.dumps({'action': 'connect',
                                       'actionStatus': 'Success',
                                       'value': self.client_id}))
        self.LOGGER.debug("Clients Set: {}".format(self.clients_address))
      
    def on_message(self, message):
        self.LOGGER.debug('Received: {}'.format(message))

        message = json.loads(message)
        action = message['action']
        value = message['value']
        
        if action == 'identify':
            secret_key = self.config['SERVER']['SECRET_KEY']
            if hash(secret_key) == value:
                self.server_address[self.client_id] = self
                self.write_message(json.dumps({'action': action,
                                               'actionStatus': 'Success',
                                               'value': self.client_id}))
            else:
                self.write_message(json.dumps({'action': action,
                                               'actionStatus': 'Failure'}))

    def on_close(self):
        self.clients_address.pop(self.client_id, None)
        self.LOGGER.info('Connection closed...')
 
    def check_origin(self, origin):
        return True