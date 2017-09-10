# -*- coding: utf-8 -*-
import requests
import json
import csv
import time
import re
from CrawlClient import Crawler
from lxml import etree
class CFCrawler(Crawler.Crawler):
    def __init__(self, max_try_cnt, url = 'http://codeforces.com'):
        self.try_cnt = 0
        self.max_try_cnt = max_try_cnt
        self.url = url
        self.rows = []
        self.try_second = 10

    def crawl(self):
        print("正在从 CodeForces抓取数据...")
        begin_time = time.time()
        #print("Vol 66 ".find("Vol 66 "))
        volume_cnt = 1
        while True:
            #Crawler.Crawler.progressbar(volume_cnt, 38)
            print("正在抓取CF volume %d .." % volume_cnt)
            url = self.url + "/problemset/page/%d" % volume_cnt
            while True:
                try:
                    u = requests.get(url, headers= None)
                    break
                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                    print("请求失败，%ds 后重试" % self.try_second)
                    time.sleep(self.try_second)
            # with open("column.html", "r", encoding="utf-8") as f:
            #     data = f.read()
            html = etree.HTML(u.text)
            vol_id = int(html.xpath('//*[@id="pageContent"]/div[3]/ul/li//a//text()')[-2])
            if volume_cnt > vol_id:
                break
            cnt = 2
            while True:
                problem = html.xpath('//*[@id="pageContent"]/div[2]/div[6]/table/tr[%d]' % cnt)
                if not problem:
                    break
                #print(type(problem[0]))

                pro_id = str(problem[0].xpath("td[1]//a/text()")[0]).strip()
                pro_title = str(problem[0].xpath("td[2]/div/a/text()")[0]).strip()
                try:
                    ac_user = problem[0].xpath("td[4]/a/text()")[0]
                except IndexError:
                    ac_user = 0
                item = []
                item.append("CodeForces")
                item.append(pro_id)
                item.append(pro_title)
                item.append(ac_user)
                item.append("")
                item.append("")
                item.append("")
                self.rows.append(item)
                #print(pro_id, pro_title)
                cnt = cnt + 1
            volume_cnt = volume_cnt + 1
        end_time = time.time()

        print("抓取完成，耗时" ,time.strftime("%M:%S", time.localtime(end_time - begin_time)))

        return True

    def save(self, filename):
        headers = ["OJ", "Problem Number", "Problem Title", "AC Users", "Try Users", "AC Submission",
                   "All Submission"]
        with open(filename, "wt", encoding="utf-8") as f:
            f_csv = csv.writer(f, lineterminator='\n')
            f_csv.writerow(headers)
            f_csv.writerows(self.rows)