# -*- coding: utf-8 -*-
import requests
import json
import csv
import time
import re
import threading
from CrawlClient import Crawler
from lxml import etree
class HDUCrawler(Crawler.Crawler):
    def __init__(self, max_try_cnt, url = 'http://acm.hdu.edu.cn'):
        self.try_cnt = 0
        self.max_try_cnt = max_try_cnt
        self.url = url
        self.rows = []
        self.try_second = 10
        self.id_to_title = dict()
        self.max_threads = 15
    def crawl_column(self,cur_volume):
        self.id_to_title.clear()
        url = self.url + "/listproblem.php?vol=%d" % cur_volume
        print("正在抓取HDU volume %d .." % cur_volume)
        try:
            u = requests.get(url, headers= None)
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            return -1
        # with open("column.html", "r", encoding="utf-8") as f:
        #     data = f.read()
        data = u.text
        pattern = re.compile(r"p\(\d.*?;")  # 用于提取解决数信息
        strpattren = re.compile(r"\".*\"")
        for single in pattern.findall(data):
            self.id_to_title[int(single[2:-3].split(',')[1])] = str(strpattren.findall(single)[0][1:-1].replace(r"\\","[][]").replace('\\', '').replace("[][]","\\"))
            # if int(single[2:-3].split(',')[1]) == 1177:
            #     print(self.id_to_title[int(single[2:-3].split(',')[1])])
            #     raise "sd"
        if len(self.id_to_title):
            return 1
        else:
            return 0

    def crawl(self):
        begin_time = time.clock()
        pattern = re.compile(r"<font color=white>.*?</font>")
        numpattren = re.compile(r"[0-9]+")
        if self.try_cnt == 0:
            print("正在从 HDU抓取数据...")
        self.try_cnt = self.try_cnt + 1
        #try:
        cur_volume = 1
        while True:
            #Crawler.Crawler.progressbar(cur_volume,53)
            state = self.crawl_column(cur_volume)
            crawl_queue = list(self.id_to_title)
            if state == -1:
                print("网络故障，抓取失败")
                return False
            elif state == 0:
                break
            url = self.url + "/statistic.php?pid="
            def process_queue():
                try:
                    problem_id = crawl_queue.pop()
                    problem_title = self.id_to_title[problem_id]
                    item = []
                    item.append("HDU")
                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
                    #print(url + problem_id)
                    print("正在抓取HDU：%d - %s" % (problem_id, problem_title) )
                    while True:
                        try:
                            u = requests.get(url + str(problem_id), headers= headers)
                            data = u.text
                            break
                        except  (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                            print("请求失败，%ds 后重试" % self.try_second)
                            time.sleep(self.try_second)
                            continue


                    raw_result_list = pattern.findall(data)
                    result_list = []
                    for raw_result in raw_result_list:
                        #print(raw_result)
                        result_list.append(numpattren.findall(raw_result)[0])
                    #html = etree.HTML(data)
                    #values = html.xpath("/html/body/table/tr[4]/td/table/tr/td[1]/table/tr//font/text()")[0:3]
                    #problem_id = html.path("/html/body/table/tr[4]/td/table/tr/td[2]/h1/a/text()")[0].split(' ')[1]
                    item.append(problem_id) #添加问题标题
                    item.append(problem_title) #添加问题标题
                    item.append(result_list[1]) # 添加解决用户数
                    item.append("") # 添加总用户数
                    item.append(result_list[2]) #添加AC提交数
                    item.append(result_list[0]) #添加总提交数
                    self.rows.append(item)
                    #print(problem_id, "End")
                    return True

                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                    print("网络故障，抓取失败")
                    return False
            threads = []
            while threads or crawl_queue:
                cnt = 0
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)
                    #else:
                        #print("alive = %d" % cnt)
                while len(threads) < self.max_threads and crawl_queue:
                    #print(len(threads))
                    thread = threading.Thread(target=process_queue)
                    thread.setDaemon(True)
                    thread.start()
                    threads.append(thread)
            cur_volume = cur_volume + 1
        end_time = time.clock()
        print("抓取完成，耗时" , time.strftime("%M:%S", time.localtime(end_time - begin_time)))
        return True

    def save(self, filename):
        headers = ["OJ", "Problem Number", "Problem Title", "AC Users", "Try Users", "AC Submission",
                   "All Submission"]
        with open(filename, "wt", encoding="GBK") as f:
            f_csv = csv.writer(f, lineterminator='\n')
            f_csv.writerow(headers)
            f_csv.writerows(self.rows)