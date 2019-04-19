from scrapper.scrapper import scrapper
from websocket.ws_server import WSServer

import time
import os
import simplejson as json
import logging
import configparser
import json

class scheduledScrapper():

	LOGGER = logging.getLogger(__name__)
	config = configparser.ConfigParser()
	config = configparser.ConfigParser()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	path = os.path.join(dir_path, '..', '..', 'conf', 'config.ini')
	config.read(path)

	def __init__(self):
		self.__ticker_symbols = ['aapl']
		self.__within_hours = self.config['SCRAPPER']['WITHIN_HOURS']
		self.__sleep_time_s = self.config['SCRAPPER']['SLEEP_TIME']

		self.__queued_ticker_symbol = []
		self.__news_source = ''
		self.__news_source_unique_names = ['cnbc', 'benzinga_headlines', 'benzinga_partner', 'benzinga_press']
		# For cases where we want to scrape from multiple sections of the same site
		# Eg: Benzinga headline, Benzinga press-release
		self.__walking_pattern_xpath = ''
		self.__headline_pattern_xpath = ''
		self.__date_pattern_xpath = ''

		self.__log_dir = './log'
		# Saved on RAM
		# Move later to designated database if need be
		self.__result_set = {}
		self.__most_recent_news = {}
		super(scheduledScrapper, self).__init__()

	def run(self):
		if not os.path.exists(self.__log_dir):
			os.makedirs(self.__log_dir)

		while True:
			current_time = int(time.time())

			for ticker_symbol in self.__ticker_symbols:
				ticker_symbol = ticker_symbol.upper()
				output_file_name = "{}.json".format(current_time)

				# Inject necessary data into object and scrape
				for source_unique_name in self.__news_source_unique_names:
					source_unique_name = source_unique_name.upper()
					try:
						self.build_variables_by_values(source_unique_name, ticker_symbol)
						self.LOGGER.info("Scrapping {} news from {} into {}".format(ticker_symbol, self.__news_source, output_file_name))
						self.scrape_with_ticker(source_unique_name, ticker_symbol)
					except Exception as e:
						self.LOGGER.error("Failed to scrape from {} with exception {}, check if designated site is online".format(self.__news_source, e))
						continue

			# Write new updates to file
			if len(self.__result_set) > 0:
				with open(os.path.join(self.__log_dir, output_file_name), 'w') as f:
					json.dump(self.__result_set, f)
				self.LOGGER.info("Scrapping finished, sleeping for {}s".format(self.__sleep_time_s))
			else:
				self.LOGGER.info("No news since last scrapping session, sleeping for {}s".format(self.__sleep_time_s))

			# Clean result set, update ticker symbol list for next scrapping session
			self.__result_set = {}
			self.update_ticker_symbol_list()
			time.sleep(self.__sleep_time_s)

	def scrape_with_ticker(self, source_unique_name, ticker_symbol):
		try:
			web_scrapper = scrapper(news_source=self.__news_source,
									ticker_symbol=ticker_symbol, 
									walking_pattern_xpath=self.__walking_pattern_xpath, 
									headline_pattern_xpath=self.__headline_pattern_xpath,
									within_hours=self.__within_hours, 
									date_pattern_xpath=self.__date_pattern_xpath, 
									require_sentiment=True)
			web_scrapper.scrape()
			results = web_scrapper.results

			parsed_result_set = []
			latest_news_timestamp = self.get_latest_news_timestamp(source_unique_name, ticker_symbol)
			
			for headline in results:
				if headline['date'] > latest_news_timestamp:
					parsed_result_set.append({key: value for key, value in headline.items()})

			# Update result set
			if len(parsed_result_set) > 0: self.__result_set[ticker_symbol][source_unique_name] = parsed_result_set
			# Set latest news timestamp for next scrapping sessions
			self.set_latest_news_timestamp(source_unique_name=source_unique_name, 
										   ticker_symbol=ticker_symbol, 
										   scrape_results=results)

		except Exception as e:
			self.LOGGER.error("Failed to scrape from source {} with exception: {}".format(self.__news_source, e))
			return
	
	def update_ticker_symbol_list(self):
		"""
		Update list of ticker symbols after each scrapping session
		"""
		self.__ticker_symbols.extend([ticker_symbol for ticker_symbol in self.__queued_ticker_symbol if ticker_symbol not in self.__ticker_symbols])

	def add_ticker_symbol(self, ticker_symbol):
		"""
		Queue ticker symbol to be added to self.__ticker_symbol in the next consecutive scrapping iteration
		"""
		if ticker_symbol not in self.__queued_ticker_symbol:
			self.__queued_ticker_symbol.append(ticker_symbol)

	def get_latest_news_timestamp(self, source_unique_name, ticker_symbol):
		return self.__most_recent_news[source_unique_name][ticker_symbol]

	def set_latest_news_timestamp(self, source_unique_name, ticker_symbol, scrape_results):
		latest_news_timestamp = max([headline['date'] for headline in scrape_results]) if len(scrape_results) > 0 else float('-inf')

		if latest_news_timestamp > self.get_latest_news_timestamp(source_unique_name, ticker_symbol):
			self.__most_recent_news[source_unique_name][ticker_symbol] = latest_news_timestamp

	def build_variables_by_values(self, source_unique_name, ticker_symbol):
		"""
		Prepare values for variables required for scrapping and data storage
		"""
		source_unique_name = source_unique_name.upper()
		self.__news_source = self.config['NEWS_PATTERN']['{}_NEWS_SOURCE'.format(source_unique_name)]
		self.__walking_pattern_xpath = self.config['NEWS_PATTERN']['{}_WALKING_PATTERN'.format(source_unique_name)]
		self.__headline_pattern_xpath = self.config['NEWS_PATTERN']['{}_HEADLINE_PATTERN'.format(source_unique_name)]
		self.__date_pattern_xpath = self.config['NEWS_PATTERN']['{}_DATE_PATTERN'.format(source_unique_name)]

		# Prepare dictionary keys
		if source_unique_name not in self.__most_recent_news.keys():
			self.__most_recent_news[source_unique_name] = {}
		if ticker_symbol not in self.__most_recent_news[source_unique_name]:
			self.__most_recent_news[source_unique_name][ticker_symbol] = float('-inf')
		if ticker_symbol not in self.__result_set:
			self.__result_set[ticker_symbol] = {}