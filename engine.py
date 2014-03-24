#-*- coding:UTF-8 -*-

import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import util
import searchdb
import re

logger = util.getLogger(__name__)

ignoreWords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class Crawler:

    """Crawler class """

    def __init__(self):
        self.db = searchdb.SearchDb()

    def addToIndex(self, url, soup):
        if self.isIndexed(url):
            return
        logger.info('indexing %s' % url)

        text = self.getTextOnly(soup)
        words = self.separateWords(text)
        wlen = len(words)

        urlItem = self.db.getUrl(url)
        if urlItem is None:
            urlId = self.db.addUrl(url)
            if urlId is None:
                logger.error(u'url add to index failed', exc_info=True)
                return
        else:
            urlId = urlItem['_id']

        for i in range(wlen):
            word = words[i]
            if word in ignoreWords:
                continue
            wordItem = self.db.getWord(word)
            if wordItem is None:
                wordId = self.db.addWord(word)
                if wordId is None:
                    logger.error(u'add word to index failed', exc_info=True)
                    continue
            else:
                wordId = wordItem['_id']

            self.db.addWordLocation(urlId, wordId, i)

    def getTextOnly(self, soup):
        v = soup.string
        if v is None:
            c = soup.contents
            resultText = ''
            for t in c:
                subtext = self.getTextOnly(t)
                resultText += subtext + '\n'
            return resultText
        else:
            return v.strip()

    def separateWords(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']

    def isIndexed(self, url):
        return self.db.hasUrlAndWords(url)

    def addLinkRef(self, urlFrom, urlTo, linkText):
        logger.info(u'add link {} to url {}'.format(urlTo, urlFrom))

        urlFromItem = self.db.getUrl(urlFrom)
        # add url into database and generate urlId
        urlId = self.db.addUrl(urlTo)
        if urlId is None:
            return
        # add word into database and generate wordId
        wordId = self.db.addWord(linkText)
        if wordId is None:
            return

        self.db.addLinkToUrl(urlFromItem['_id'], urlId, wordId)

    def crawl(self, pages, depths=2):
        for i in range(depths):
            newPages = set()
            for page in pages:
                logger.info(u'crawling page {}'.format(page))
                try:
                    c = urllib2.urlopen(page)
                except Exception as e:
                    logger.error(
                        u'open page {} failed'.format(page), exc_info=True)
                    continue

                soup = BeautifulSoup(c.read())

                self.addToIndex(page, soup)

                links = soup('a')
                for link in links:
                    logger.info(u'link {}'.format(link))
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        logger.info(u'href {}'.format(url))
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.isIndexed(url):
                            newPages.add(url)
                        linkText = self.getTextOnly(link)
                        self.addLinkRef(page, url, linkText)

                pages = newPages


class Searcher:

    """docstring for Searcher"""

    def __init__(self):
        self.db = searchdb.SearchDb()

    def _addWordLocationToDic(self, dic, wordLocations):
        for wl in wordLocations:
            key = wl['urlId']
            value = dic.get(key)
            if value is None:
                value = []

            value.append(wl)
            dic[key] = value

    def _aggregateWordLocations(self, dic):
        result = []
        for urlId, wls in dic.iteritems():
            locs = []
            locs.append(urlId)
            for wl in wls:
                locs.append(wl['location'])

            result.append(locs)

        return result

    def getMatchUrls(self, q):
        words = q.split(' ')

        wordItems = self.db.getWords(words)
        wordIds = [w['_id'] for w in wordItems]

        wordLocs = self.db.getDb().wordlocations.find(
            {'wordId': wordIds[0]}, {'_id': 0})

        if wordLocs is None:
            return None

        wordDic = {}
        self._addWordLocationToDic(wordDic, wordLocs)

        for wd in wordIds[1:]:
            if wordLocs is None or wordLocs.count() == 0:
                break

            urlIds = [wl['urlId'] for wl in wordLocs]
            wordLocs = self.db.getDb().wordlocations.find(
                {'urlId': {'$in': urlIds}, 'wordId': wd}, {'_id': 0})

            self._addWordLocationToDic(wordDic, wordLocs)

        return self._aggregateWordLocations(wordDic), wordIds

    def getScoredList(self, wordLocs, wordIds):
        totalScores = dict([(wl[0], 0) for wl in wordLocs])

        weights = [(1.0, self.frequencyScore(wordLocs)),
                   (1.5, self.locationScore(wordLocs)),
                   (1.0, self.distanceScore(wordLocs))]

        for (weight, scores) in weights:
            for url in totalScores:
                totalScores[url] += weight * scores[url]

        return totalScores

    def normalizeScores(self, scores, small=False):
        vsmall = 0.00001
        if small:
            minscore = min(scores.values())
            return dict([(u, float(minscore) / max(vsmall, c)) for u, c in scores.items()])
        else:
            maxscore = max(scores.values())
            if maxscore == 0:
                maxscore = vsmall
            return dict([(u, float(c) / maxscore) for u, c in scores.items()])

    def frequencyScore(self, wordLocs):
        counts = dict([(wl[0], 0) for wl in wordLocs])
        for wl in wordLocs:
            counts[wl[0]] = len(wl)
        return self.normalizeScores(counts)

    def locationScore(self, wordLocs):
        locations = dict([(wl[0], 1000000) for wl in wordLocs])
        for wl in wordLocs:
            loc = sum(wl[1:])
            if loc < locations[wl[0]]:
                locations[wl[0]] = loc

        return self.normalizeScores(locations, True)

    def distanceScore(self, wordLocs):
        scores = dict([(wl[0], 1000000) for wl in wordLocs])

        for wl in wordLocs:
            if len(wl)<=2:
                continue
            dist = sum([abs(wl[i] - wl[i - 1]) for i in range(2, len(wl))])
            if dist < scores[wl[0]]:
                scores[wl[0]] = dist

        return self.normalizeScores(scores, True)

    def query(self, q):
        wordLocs, wordIds = self.getMatchUrls(q)
        scores = self.getScoredList(wordLocs, wordIds)
        rankedScores = sorted([(score, url)
                              for (url, score) in scores.items()], reverse=1)

        for score, urlId in rankedScores:
            print '%f\t%s' % (score, self.db.getUrlById(urlId)['url'])
