from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket

import functools
import json
import time
import logging
import configparser
import os
import time

class WSClient():

    """
    Websocket Client base implementation
    Scheduled_scrapper's parent
    """

    config = configparser.ConfigParser()
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, '..', '..', 'conf', 'config.ini')
    config.read(path)

    LOGGER = logging.getLogger(__name__)

    def __init__(self, *, connect_timeout=60, request_timeout=60):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._ws_connection = None
        self.__secret_key = self.config['SERVER']['SECRET_KEY']
        self.__uuid = None

    def connect(self, url):
        headers = httputil.HTTPHeaders({'Content-Type': self.config['WEBSOCKET_CLIENT']['APPLICATION_JSON']})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(ioloop.IOLoop.current(), request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def identify_self(self):
        """
        Identify as automated webscrapper
        """
        data = {'action': 'identify',
                'value': hash(self.__secret_key)}

        while True:
            if not self._ws_connection: time.sleep(1)
            break

        self._ws_connection.write_message(escape.utf8(json.dumps(data)))

    def send(self, data):
        while True:
            if not self._ws_connection: time.sleep(1)
            break

        self._ws_connection.write_message(escape.utf8(json.dumps(data)))

    def close(self):
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break
            self._on_message(msg)

    @gen.coroutine
    def _on_message(self, msg):
        self.LOGGER.debug("MSG: {}".format(msg))
        msg = json.loads(msg)
        action = msg['action']
        action_status = msg['actionStatus']

        value = msg['value'] if action_status == 'Success' else None

        if action == 'identify':
            self.__uuid = value

    def _on_connection_success(self):
        self.LOGGER.info('Connected!')

    def _on_connection_close(self):
        self.LOGGER.info('Connection closed!')

    def _on_connection_error(self, exception):
        self.LOGGER.info('Connection error: {}'.format(exception))
