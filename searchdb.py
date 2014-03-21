#-*- coding:UTF-8 -*-

import util
import pymongo
from pymongo import MongoClient

logger = util.getLogger(__name__)


class SearchDb(object):

    """docstring for SearchDb"""

    def __init__(self, host='localhost', port='27017'):
        super(SearchDb, self).__init__()
        self.host = host
        self.isConnected = False
        self.db = None
        self.port = port
        self.url = 'mongodb://{}:{}/'.format(host, port)

    def _connect(self):
        client = MongoClient(self.url)
        logger.info('connecting to {}'.format(self.url))

        self.db = client.textsearch

    def _verifyConnection(self):
        if self.isConnected:
            return self.isConnected

        try:
            self._connect()
        except Exception as e:
            self.isConnected = False
            logger.error(
                'can not connect to mongodb {}'.format(self.url), exc_info=True)
        else:
            self.isConnected = True

        return self.isConnected

    def getUrl(self, url):
    	self._verifyConnection()

        try:
            return self.db.urls.find_one({'url': url})
        except Exception as e:
            logger.error(
                u'get url by {} from database error'.format(url), exc_info=True)
            return None
    def getUrlById(self,urlId):
        try:
            return self.db.urls.find_one({'_id':urlId})
        except Exception, e:
            logger.error(u'get url by id {} error'.format(urlId),exc_info=True)
            return None

    def addUrl(self, url):
    	if not self._verifyConnection(): return 

        try:
            return self.db.urls.insert({'url': url,'links':[]})
        except Exception as e:
            logger.error(
                u'add url {} to database error'.format(url), exc_info=True)
            return None

    def addLinkToUrl(self,urlId,linkId,wordId):
        if not self._verifyConnection(): return

        try:
            urlItem = self.db.urls.find_one({'_id':urlId})
            if urlItem is None:
                logger.warnings('can not find url {} in database'.format(urlId))
                return

            # link = [ l for l in urlItem['links'] if l.linkId==linkId and l.wordId==wordId]
            # if link is None:
            #     urlItem['links'].append({'urlId':linkId,'wordId':wordId})
            #     #replace the item with new values
            #     self.db.urls.save(urlItem)

            self.db.urls.update({'_id':urlId},{'$addToSet':{'links':{'urlId':linkId,'wordId':wordId}}})

        except Exception, e:
            logger.error('add link to url error',exc_info=True)

    def getDb(self):
        if not self._verifyConnection(): return

        return self.db        

    def addWord(self, word):
    	if not self._verifyConnection(): return

        try:
            return self.db.words.insert({'word': word})
        except Exception, e:
            logger.error(
                u'add word {} to database error'.format(word), exc_info=True)
            return None

    def getWord(self, word):
    	if not self._verifyConnection(): return

        try:
            return self.db.words.find_one({'word': word})
        except Exception, e:
            logger.error(
                u'get word {} from database error'.format(word), exc_info=True)
            return None

    def getWords(self,words):
        if not self._verifyConnection(): return

        try:
            return self.db.words.find({'word':{'$in':words}})
        except Exception, e:
            logger.error(u'get words error',exc_info=True)
            return None


    def addWordLocation(self, urlId, wordId, location):
    	if not self._verifyConnection(): return

        try:
            self.db.wordlocations.insert({'urlId':urlId,'wordId':wordId,'location':location})
        except Exception, e:
            logger.error(
                u'add word {} location error'.format(wordId), exc_info=True)

    def hasUrlAndWords(self, url):
    	if not self._verifyConnection(): return

        try:
            urlItem = self.getUrl(url)
            if urlItem is None:
                return False

            count = self.db.wordlocations.find({'urlId': urlItem['_id']}).count()
            return count > 0
        except Exception, e:
            logger.error(
                u'call hasUrlAndWords with url {} error'.format(url), exc_info=True)
            return False

    def clear(self):
        if not self._verifyConnection(): return

        self.db.urls.remove()
        self.db.words.remove()
        self.db.wordlocations.remove()
