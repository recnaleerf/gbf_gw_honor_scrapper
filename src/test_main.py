from controller.scrapper_controller import scrapper_controller
from flask import Flask
import configparser, os
import logging.config
import yaml
import argparse

import socket
import signal
import tornado
import threading
import time
from websocket.ws_handler import WSHandler
from websocket.ws_server import WSServer
from websocket.ws_client import WSClient

from scrapper.scrapper import scrapper
from scrapper.scheduled_scrapper import scheduledScrapper

from dateutil.parser import *

app = Flask(__name__)

config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, '..', 'conf', 'config.ini')
config.read(path)

def run_config():
	path = os.path.join('conf', 'logging.yaml')
	value = os.getenv('LOG_CFG', None)
	if value:
		path = value
	if os.path.exists(path):
		with open(path, 'rt') as f:
			config = yaml.safe_load(f.read())
		logging.config.dictConfig(config)
	else:
		logging.basicConfig(level=default_level)

def start_backend_server():
	app.register_blueprint(scrapper_controller)
	app.run(host=config['SERVER']['HOST'], 
			port=config['SERVER']['PORT'], 
			threaded=True,
			debug=True)

def start_automated_scrapper(within_hours, sleep_time_s):
	scheduled_scrapper = scheduledScrapper(within_hours=within_hours, 
										   sleep_time_s=sleep_time_s)

	e = threading.Event()
	scrapper_thread = threading.Thread(target=scheduled_scrapper.run, args=[])
	scrapper_thread.start()

# if __name__ == "__main__":
# 	parser = argparse.ArgumentParser(description='Stock news webscrapper & sentiment analysis')
# 	parser.add_argument('mode', type=int, help='Scrapper mode, 1 to start backend API server, 2 to start automated scheduled scrapper')
# 	parser.add_argument('--within', default=24, metavar='WITHIN', type=int, help='Scrape only news within <hrs>')
# 	parser.add_argument('--sleep', default=60, metavar="SLEEP", type=int, help='Sleep time in (s) after each iteration of web scrapping')

# 	args = parser.parse_args()

# 	# Setup logging config
# 	run_config()

# 	# Start service
# 	if args.mode == 1:
# 		start_backend_server()

# 	elif args.mode == 2:
# 		within_hours = args.within
# 		sleep_time_s = args.sleep
# 		start_automated_scrapper(within_hours=within_hours,
# 								 sleep_time_s=sleep_time_s)

if __name__ == '__main__':
	run_config()

	ws_ip = socket.gethostbyname(socket.gethostname())
	ws_route = config['WEBSOCKET_SERVER']['ROUTE']
	ws_port = config['WEBSOCKET_SERVER']['PORT']

	application = scheduledScrapper()
	tornado.options.parse_command_line()
	signal.signal(signal.SIGINT, application.signal_handler)
	application.listen(ws_port)

	print('Websocket Server Started at ws://{}:{}{}'.format(ws_ip, ws_port, ws_route))
	tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
	# tornado.ioloop.IOLoop.instance().start()
	
	tornado_thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start)
	tornado_thread.start()

	# client = scheduledScrapper(within_hours=24, sleep_time_s=10)
	# client.connect('ws://{}:{}{}'.format(ws_ip, ws_port, ws_route))
	# client.run()
	# client.send("HELLO SERVER@@@@")