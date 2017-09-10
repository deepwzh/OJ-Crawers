# -*- coding: utf-8 -*-
from CrawlClient.UVaCrawler import UVaCrawler
from CrawlClient.POJCrawal import POJCrawler
from CrawlClient.ZOJCrawler import ZOJCrawler
from CrawlClient.CFCraweler import CFCrawler
from CrawlClient.HDUCrawler import HDUCrawler


class CrawlerFactory(object):
    def __init__(self):
        pass
    def getCrawler(self, oj):
        if oj == "POJ":
            return (POJCrawler(3))
        elif oj == "ZOJ":
            return (ZOJCrawler(3))
        elif oj == "CF":
            return (CFCrawler(3))
        elif oj == "UVA":
            return (UVaCrawler(3))
        elif oj == "HDU":
            return (HDUCrawler(3))
