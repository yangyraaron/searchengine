#-*- coding: UTF-8 -*-


import logging
import logging.config
import settings
import util
import engine

logging.config.dictConfig(settings.logging)
logger = util.getLogger()

class Application:
	"""docstring for Application"""
	def __init__(self):
		logger.info('initializing applicaiton')

	def buildEnv(self):
		logger.info('buiding environment')

	def run(self):
		searcher = engine.Searcher()
		searcher.query('list append')


def main():
	app = Application()
	logger.info('application is running')
	app.run()


if __name__ == "__main__":
	main()