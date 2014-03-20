#-*- coding: UTF-8 -*-


import logging
import settings
import os

def getLogger(name=''):
	if name.strip == '':
		return logging.getLogger(settings.app['name'])

	return logging.getLogger(settings.app['name']+'.'+name)

logger = getLogger(__name__)


def verifyExists(dirPath):
	try:
		if not os.path.exists(dirPath):
			os.mkdirs(dirPath)
	except Exception as e:
		logger.error(u'verify exists of the directory {} failed'.format(dirPath),exc_info=True)