#-*- coding: utf-8 -*-
import http
from pprint import pprint
import json
import requests
#from urllib import request, parse, error
import json
import csv
import time
import threading
from CrawlClient.CrawlerFactory import CrawlerFactory

"""
Problem ID
Problem Number
Problem Title
Number of Distinct Accepted User (DACU)
Best Runtime of an Accepted Submission
Best Memory used of an Accepted Submission
Number of No Verdict Given (can be ignored)
Number of Submission Error
Number of Can't be Judged
Number of In Queue
Number of Compilation Error
Number of Restricted Function
Number of Runtime Error
Number of Output Limit Exceeded
Number of Time Limit Exceeded
Number of Memory Limit Exceeded
Number of Wrong Answer
Number of Presentation Error
Number of Accepted
Problem Run-Time Limit (milliseconds)
Problem Status (0 = unavailable, 1 = normal, 2 = special judge)
"""

def pojcrawle(pojCrawer):
    pojCrawer.crawl()
    pojCrawer.save("result\\poj.csv")

def hducrawle(hduCrawer):
    hduCrawer.crawl()
    hduCrawer.save("result\\hdu.csv")

def main():
    begin_time = time.clock()
    fact = CrawlerFactory()
    uvaCrawer = fact.getCrawler("UVA")
    cfCrawer = fact.getCrawler("CF")
    zojCrawer = fact.getCrawler("ZOJ")
    hduCrawer = fact.getCrawler("HDU")
    pojCrawer = fact.getCrawler("POJ")
    uvaCrawer.crawl()
    uvaCrawer.save("result\\uva.csv")
    cfCrawer.crawl()
    cfCrawer.save("result\\cf.csv")
    zojCrawer.crawl()
    zojCrawer.save("result\\zoj.csv")
    hduthread = threading.Thread(target=hducrawle, args=(hduCrawer, ))
    hduthread.setDaemon(True)
    hduthread.start()
    pojthread = threading.Thread(target=pojcrawle, args=(pojCrawer, ))
    pojthread.setDaemon(True)
    pojthread.start()
    while hduthread or pojCrawer:
        pass
    print("抓取完成")
    end_time = time.clock()
    print("抓取完成，总耗时", time.strftime("%M:%S", time.localtime(end_time - begin_time)))


    # crawler = POJCrawler(3)
    # if crawler.threaded_crawl():
    #     crawler.save("poj3.csv")
    # querystring = parse.urlencode(parms)
    #crawler = UVaCrawler(3)
    #data = crawler.crawl()
    #if data is None:
    #     return
    # crawler.save("uva-crawling.csv")
    # print(rows[2])

    # with open ( 'something.json', 'wt' ) as f:
    #     json.dump ( data, f )


if __name__ == '__main__':
    main()