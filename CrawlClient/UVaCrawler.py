# -*- coding: utf-8 -*-
import requests
import json
import csv

from CrawlClient import Crawler

class UVaCrawler(Crawler.Crawler):
    def __init__(self, max_try_cnt, url = 'http://uhunt.onlinejudge.org/api/p'):
        self.try_cnt = 0
        self.max_try_cnt = max_try_cnt
        self.url = url
        self.rows = []

    def crawl(self):
        if self.try_cnt == 0:
            print("Crawling Data from Uva...")
        self.try_cnt = self.try_cnt + 1
        try:
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
            u = requests.get(self.url)
            data = json.loads(u.text)
            self.rows.clear()
            for line in data:
                # print(i, line)
                item = []
                item.append("UVA")  # OJ Name
                item.append(line[1])  # ID
                item.append(line[2])  # Title
                item.append(line[3])  # Distinct Accepted User
                item.append("")
                item.append(line[18])  # Number Accept
                cnt = 0
                for i in range(10, 19):
                    cnt = cnt + line[i]
                item.append(cnt)  # Number submission
                self.rows.append(item)
            print("Crawl Successful~")
            self.try_cnt = 0
            return True
        except (requests.exceptions.RequestException, ):
            if self.try_cnt <= self.max_try_cnt:
                print("Crawl Try %d/%d~" % (self.try_cnt, self.max_try_cnt))
                self.crawl()
            else:
                print("Crawl Fail~")
                self.try_cnt = 0
                return None

    def save(self, filename):
        headers = ["OJ", "Problem Number", "Problem Title", "AC Users", "Try Users", "AC Submission",
                   "All Submission"]
        with open(filename, "wt", encoding="utf-8") as f:
            f_csv = csv.writer(f, lineterminator='\n')
            f_csv.writerow(headers)
            f_csv.writerows(self.rows)