# -*- coding: utf-8 -*-
import requests
import json
import csv
import time
import re
import threading
from CrawlClient import Crawler
from lxml import etree

class POJCrawler(Crawler.Crawler):
    def __init__(self, max_try_cnt, url = 'http://poj.org'):
        self.try_cnt = 0
        self.max_try_cnt = max_try_cnt
        self.url = url
        self.rows = []
        self.try_second = 10
        self.id_to_title = dict()
        self.cur_volume = 2
        self.max_threads = 13

    def crawl_column(self, cur_volume):
        self.id_to_title.clear()
        url = self.url + "/problemlist?volume=%d" % cur_volume
        print("正在抓取POJ volume %d .." % cur_volume)
        try:
            u = requests.get(url, headers= None)
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            return -1
        # with open("column.html", "r", encoding="utf-8") as f:
        #     data = f.read()
        html = etree.HTML(u.text)
        cnt = 2
        while True:
            problem = html.xpath('/html/body/table[2]/tr[%d]' % cnt)
            if not problem:
                break
            #print(type(problem[0]))

            pro_id = problem[0].xpath("td[1]/text()")[0]
            pro_title = str(problem[0].xpath("td[2]/a/text()")[0]).replace('\r\n', ' ')
            self.id_to_title[int(pro_id)] = pro_title
            #print(pro_id, pro_title)
            cnt = cnt + 1
        if cnt == 2:
            return 0
        else:
            return 1

    def crawl(self):
        begin_time = time.clock()
        num_parttern = re.compile(r'\d+')  # 用于提取数字
        # pattern = re.compile(r'sa\[[0-9]\]\[[0-9]\]=\'[A-Z][A-Za-z ]*\'*')
        cnt_pattern = re.compile(r'sa\[[0-9]\]\[[0-9]\]=[0-9]+')  # 用于提取解决数信息
        id_pattern = re.compile(r'problem_id=\d+')  # 用于提取题号
        pattern = re.compile(r"\d*,\d*,'statu")  # 用于提取解决数信息
        if self.try_cnt == 0:
            print("\n正在从 POJ抓取数据...")
        self.try_cnt = self.try_cnt + 1
        #/html/body/table[2]/tbody/tr/td[1]/div/table/tbody/tr[1]/td[2]/a
        #try:
        # /html/body/center
        #cur_volume = 1
        cur_volume = 1
        while True:
            #Crawler.Crawler.progressbar(cur_volume, 32)
            state = self.crawl_column(cur_volume)
            if state == -1:
                print("网络故障，抓取失败")
                return False
            elif state == 0:
                break
            crawl_queue = list(self.id_to_title)
            # with open("poj.html", "r") as f:
            #     data = f.read()

            url = self.url + "/problemstatus?problem_id="
            def process_queue():
                try:
                    problem_id = crawl_queue.pop()
                    problem_title = self.id_to_title[problem_id]
                    item = []
                    item.append("POJ")
                    headers = {
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
                    # print(url + problem_id)
                    print("正在抓取POJ：%d - %s" % (problem_id, problem_title))
                    while True:
                        try:
                            u = requests.get(url + str(problem_id), headers=headers)
                            data = u.text
                            break
                        except  (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                            print("请求失败，%ds 后重试" % self.try_second)
                            time.sleep(self.try_second)
                            continue
                    match1 = pattern.findall(data)
                    match2 = cnt_pattern.findall(data)
                    match3 = id_pattern.findall(data)
                    if match1 and match2 and match3:
                        self.problem_id = num_parttern.findall(match3[0])[0]  # 抓取问题id
                        item.append(problem_id)  # 添加问题标题
                        item.append(problem_title)  # 添加问题标题
                        user_submitted_solved = num_parttern.findall(match1[0])  # 抓取解决用户数
                        # print(user_submitted_solved)
                        item.append(user_submitted_solved[1])  # 添加解决用户数
                        item.append(user_submitted_solved[0])  # 添加总用户数
                        # print(match2)
                        submited_cnt = num_parttern.findall(match2[0])
                        accept_submited_cnt = submited_cnt[2]  # 抓取AC提交数
                        allcnt = 0
                        for temp in match2:  # 计算总提交数
                            submited_cnt = num_parttern.findall(temp)
                            allcnt = allcnt + int(submited_cnt[2])
                        #print ("POJ", accept_submited_cnt, allcnt)
                        item.append(accept_submited_cnt)  # 添加AC提交数
                        item.append(allcnt)  # 添加总提交数
                    else:
                        print("匹配失败，可能的原因是网站更新了网页内容格式，请更新匹配算法")
                        return False
                    self.rows.append(item)
                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                    print("网络故障，抓取失败")
                    return False
            threads = []
            while threads or crawl_queue:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)
                while len(threads) < self.max_threads and crawl_queue:
                    #print("@" , len(crawl_queue), len(threads))
                    thread = threading.Thread(target=process_queue)
                    thread.setDaemon(True)
                    thread.start()
                    threads.append(thread)
                    #print("HHHHHHH")
            cur_volume = cur_volume + 1
        end_time = time.clock()
        print("抓取完成，耗时" , time.strftime("%M:%S", time.localtime(end_time - begin_time)))
        return True

    def crawl2(self):
        begin_time = time.clock()
        if self.try_cnt == 0:
            print("正在从 POJ抓取数据...")
        self.try_cnt = self.try_cnt + 1
        #/html/body/table[2]/tbody/tr/td[1]/div/table/tbody/tr[1]/td[2]/a
        #try:
        cur_volume = 1
        while True:
            state = self.crawl_column(cur_volume)
            if state == -1:
                print("网络故障，抓取失败")
                return False
            elif state == 0:
                break
            # with open("poj.html", "r") as f:
            #     data = f.read()
            num_parttern = re.compile(r'\d+')  # 用于提取数字
            # pattern = re.compile(r'sa\[[0-9]\]\[[0-9]\]=\'[A-Z][A-Za-z ]*\'*')
            cnt_pattern = re.compile(r'sa\[[0-9]\]\[[0-9]\]=[0-9]+')  # 用于提取解决数信息
            id_pattern = re.compile(r'problem_id=\d+') # 用于提取题号
            pattern = re.compile(r"\d*,\d*,'statu") #用于提取解决数信息

            url = self.url + "/problemstatus?problem_id="

            for (problem_id) in self.id_to_title:
                try:
                    problem_title = self.id_to_title[problem_id]
                    item = []
                    item.append("POJ")
                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
                    #print(url + problem_id)
                    print("正在抓取：%d - %s" % (problem_id, problem_title) )
                    while True:
                        try:
                            u = requests.get(url + str(problem_id), headers= headers)
                            data = u.text
                            break
                        except  (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                            print("请求失败，%ds 后重试" % self.try_second)
                            time.sleep(self.try_second)
                            continue

                    match1 = pattern.findall(data)
                    match2 = cnt_pattern.findall(data)
                    match3 = id_pattern.findall(data)
                    if match1 and match2 and match3:
                        self.problem_id = num_parttern.findall(match3[0])[0] # 抓取问题id
                        item.append(problem_id) #添加问题标题
                        item.append(problem_title) #添加问题标题
                        user_submitted_solved = num_parttern.findall(match1[0]) # 抓取解决用户数
                        #print(user_submitted_solved)
                        item.append(user_submitted_solved[1]) # 添加解决用户数
                        item.append(user_submitted_solved[0]) # 添加总用户数
                        #print(match2)
                        submited_cnt = num_parttern.findall(match2[0])
                        accept_submited_cnt = submited_cnt[2]  # 抓取AC提交数
                        allcnt = 0
                        for temp in match2: #计算总提交数
                            submited_cnt = num_parttern.findall(temp)
                            allcnt  = allcnt + int(submited_cnt[2])
                        #print (accept_submited_cnt, allcnt)
                        item.append(accept_submited_cnt) #添加AC提交数
                        item.append(allcnt) #添加总提交数
                    else:
                        print("匹配失败，可能的原因是网站更新了网页内容格式，请更新匹配算法")
                        return False
                    self.rows.append(item)
                except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                    print("网络故障，抓取失败")
                    return False
            cur_volume = cur_volume + 1
        end_time = time.clock()
        print("抓取完成，耗时" , time.strftime("%M:%S", time.localtime(end_time - begin_time)))
        return True

    def save(self, filename):
        headers = ["OJ", "Problem Number", "Problem Title", "AC Users", "Try Users", "AC Submission",
                   "All Submission"]
        with open(filename, "wt", encoding="utf-8") as f:
            f_csv = csv.writer(f, lineterminator='\n')
            f_csv.writerow(headers)
            f_csv.writerows(self.rows)