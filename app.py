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
		logger.info('initializing application')
	
	def _buildEnv(self):
		logger.info('build environment')
		
		util.verifyExists(settings.app['logFolder'])

	def run(self):
		crawler = engine.Crawler()
		pages = ['http://api.mongodb.org/python/2.7rc0/api/index.html']
		crawler.crawl(pages)


def main():
	app = Application()
	logger.info('application is running')
	app.run()


if __name__ == "__main__":
	main()