#-*- coding: UTF-8 -*-


import util
import logging
import logging.config
import getopt
import sys
import searchdb
import settings


logging.config.dictConfig(settings.logging)
logger = logging.getLogger('test')

db = searchdb.SearchDb()

def build():
	logger.info('building test')

def clear():
	logger.info('clearing data from database')
	db.clear()

def main():
	cmdArgs={}

	try:
		opts,args = getopt.getopt(sys.argv[1:],'t:',["type="])
	except getopt.GetoptError:
		logger.error('the commands is invalid',exc_info=True)
		sys.exit(2)

	for opt,arg in opts:
		if opt in ('-t','--type'):
			cmdArgs['type'] = arg
		else:
			assert False,"unhandled option"
	
	testType = cmdArgs.get('type')

	if testType is None:
		build()
	elif testType == 'clear':
		clear()
	
				



if __name__ == '__main__':
	main()
