#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://kesalin.github.io
# Date          : 2016/07/13
# Description   : 抓取豆瓣上指定标签的书籍并导出为 Markdown 文件，多线程版本. 
# Version       : 1.0.0.0
# Python Version: Python 2.7.3
# Python Queue  : https://docs.python.org/2/library/queue.html
# Beautiful Soup: http://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/#

import os
import time
import timeit
import datetime
import re
import string
import urllib2
import math

from threading import Thread
from Queue import Queue
from bs4 import BeautifulSoup


# 获取 url 内容
gUseCookie = True
gHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Cookie': 'Put your cookie here'
}

def getHtml(url):
    try :
        if gUseCookie:
            opener = urllib2.build_opener()
            for k, v in gHeaders.items():
                opener.addheaders.append((k, v))
            response = opener.open(url)
            data = response.read().decode('utf-8')
        else:
            request = urllib2.Request(url, None, gHeaders)
            response = urllib2.urlopen(request)
            data = response.read().decode('utf-8')
    except urllib2.URLError, e :
        if hasattr(e, "code"):
            print("The server couldn't fulfill the request: " + url)
            print("Error code: %s" % e.code)
        elif hasattr(e, "reason"):
            print("We failed to reach a server. Please check your url: " + url + ", and read the Reason.")
            print("Reason: %s" % e.reason)
    return data


# 书籍信息类
class BookInfo:
    def __init__(self, name, url, icon, num, people, comment):
        self.name = name
        self.url = url
        self.icon = icon
        self.ratingNum = num
        self.ratingPeople = people
        self.comment = comment
        self.compositeRating = num

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        if self.url == other.url:
            return True
        return False

    def __sortByCompositeRating(self, other):
        val = self.compositeRating - other.compositeRating
        if val < 0:
            return 1
        elif val > 0:
            return -1
        else:
            val = self.ratingPeople - other.ratingPeople
            if val < 0:
                return 1
            elif val > 0:
                return -1
            else:
                return 0

    def __cmp__(self, other):
        return self.__sortByCompositeRating(other)


# 导出为 Markdown 格式文件
def exportToMarkdown(filename, books, total):
    path = "{0}.md".format(filename)
    if(os.path.isfile(path)):
        os.remove(path)

    today = datetime.datetime.now()
    todayStr = today.strftime('%Y-%m-%d %H:%M:%S %z')
    file = open(path, 'a')
    file.write('\n## 我想读的书)\n\n')
    file.write('### 总计 {0:d} 本，更新时间：{1}\n'.format(total, todayStr))

    i = 0
    for book in books:
        file.write('\n### No.{0:d} {1}\n'.format(i + 1, book.name))
        file.write(' > **图书名称**： [{0}]({1})  \n'.format(book.name, book.url))
        file.write(' > **豆瓣链接**： [{0}]({1})  \n'.format(book.url, book.url))
        file.write(' > **豆瓣评分**： {0}  \n'.format(book.ratingNum))
        file.write(' > **评分人数**： {0} 人  \n'.format(book.ratingPeople))
        file.write(' > **内容简介**： {0}  \n'.format(book.comment))
        i = i + 1
    file.close()

# 解析图书信息
def parseItemInfo(minNum, maxNum, k, page, bookInfos):
    soup = BeautifulSoup(page, 'html.parser')

    # get book name
    bookName = ''
    bookImage = ''
    tag = soup.find("a", 'nbg')
    if tag != None:
        bookName = tag['title'].strip().encode('utf-8')
        bookImage = tag['href'].encode('utf-8')
    #print(" > name: {0}, bookImage: {1}".format(bookName, bookImage))

    # get description
    description = ''
    content = soup.find("div", "intro")
    if content != None:
        deses = content.find_all('p')
        for des in deses:
            if des != None and des.string != None:
                intro = des.string.strip().encode('utf-8')
                description = description + intro
    #print(" > description: {0}".format(description))

    # get book url
    bookUrl = ''
    content = soup.find("div", "indent")
    if content != None:
        tag = content.find("a")
        if tag != None:
            bookUrl = tag['href'].encode('utf-8')
            bookUrl = bookUrl.replace('/new_offer', '/')
    #print(" > url: {0}".format(bookUrl))

    ratingNum = 0.0
    ratingPeople = 0
    content = soup.find("div", "rating_self clearfix")
    if content != None:
        tag = content.find("strong", "ll rating_num ")
        if tag != None and tag.string != None:
            ratingStr = tag.string.strip().encode('utf-8')
            if len(ratingStr) > 0:
                ratingNum = float(ratingStr)
    content = soup.find("a", "rating_people")
    if content != None:
        tag = content.find('span')
        if tag != None:
            ratingStr = tag.string.strip().encode('utf-8')
            if len(ratingStr) > 0:
                ratingPeople = int(ratingStr)
    #print(" > ratingNum: {0}, ratingPeople: {1}".format(ratingNum, ratingPeople))

    # add book info to list
    bookInfo = BookInfo(bookName, bookUrl, bookImage, ratingNum, ratingPeople, description)
    bookInfo.compositeRating = computeCompositeRating(minNum, maxNum, k, ratingNum, ratingPeople)
    bookInfos.append(bookInfo)

def parseItemUrlInfo(page, urls):
    soup = BeautifulSoup(page, 'html.parser')
    items = soup.find_all("li", "subject-item")
    for item in items:
        #print(item.prettify().encode('utf-8'))

        # get item url
        url = ''
        content = item.find("div", "pic")
        if content != None:
            tag = content.find('a')
            if tag != None:
                url = tag['href'].encode('utf-8')
        #print(" > url: {0}".format(url))
        urls.append(url)

#=============================================================================
# 生产者-消费者模型
#=============================================================================
class Producer(Thread):
    url = ''
    
    def __init__(self, t_name, url, queue):  
        Thread.__init__(self, name=t_name)
        self.url = url
        self.queue = queue

    def run(self):
        page = getHtml(self.url)
        if page != None:
            # block util a free slot available
            self.queue.put(page, True)

class Consumer(Thread):
    running = True
    books = []
    queue = None
    minNum = 5
    maxNum = 5000
    k = 0.25

    def __init__(self, t_name, minNum, maxNum, k, queue, books):  
        Thread.__init__(self, name=t_name)
        self.queue = queue
        self.books = books
        self.minNum = max(10, min(200, minNum))
        self.maxNum = max(1000, min(maxNum, 20000))
        self.k = max(0.01, min(1.0, k))

    def stop(self):
        self.running = False

    def run(self):
        while True:
            if self.running == False and self.queue.empty():
                break;

            page = self.queue.get()
            if page != None:
                parseItemInfo(self.minNum, self.maxNum, self.k, page, self.books)
            self.queue.task_done()
 
class ParseItemUrlConsumer(Thread):
    running = True
    urls = []

    def __init__(self, t_name,queue, urls):  
        Thread.__init__(self, name=t_name)
        self.queue = queue
        self.urls = urls

    def stop(self):
        self.running = False

    def run(self):
        while True:
            if self.running == False and self.queue.empty():
                break;

            page = self.queue.get()
            if page != None:
                parseItemUrlInfo(page, self.urls)
            self.queue.task_done()
 

def spider(username, minNum, maxNum, k):
    print('   抓取我想读的书 ...')
    start = timeit.default_timer()

    # all producers
    queue = Queue(20)
    bookInfos = []
    producers = []

    # get first page of doulist
    wishUrl = "https://book.douban.com/people/{0}/wish".format(username)
    page = getHtml(wishUrl)
    if page == None:
        print(' > invalid url {0}'.format(wishUrl))
    else:
        # get url of other pages in doulist
        soup = BeautifulSoup(page, 'html.parser')
        content = soup.find("div", "paginator")
        #print(content.prettify().encode('utf-8'))

        nextPageStart = 100000
        lastPageStart = 0
        for child in content.children:
            if child.name == 'a':
                pattern = re.compile(r'(start=)([0-9]*)(.*)(&sort=)')
                match = pattern.search(child['href'].encode('utf-8'))
                if match:
                    index = int(match.group(2))
                    if nextPageStart > index:
                        nextPageStart = index
                    if lastPageStart < index:
                        lastPageStart = index

        # process current page
        queue.put(page)

        urls = []
        # create consumer
        consumer = ParseItemUrlConsumer('ParseItemUrlConsumer', queue, urls)
        consumer.start()

        # create parge item url producers
        # producers = []
        for pageStart in range(nextPageStart, lastPageStart + nextPageStart, nextPageStart):
            pageUrl = "https://book.douban.com/people/kesalin/wish?start={0:d}&sort=time&rating=all&filter=all&mode=grid".format(pageStart)
            producer = Producer('Producer_{0:d}'.format(pageStart), pageUrl, queue)
            producer.start()
            producers.append(producer)
            #print(" > process page : {0}".format(pageUrl))
            time.sleep(0.1)         # slow down a little

        # wait for all producers
        for producer in producers:
            producer.join()

        # wait for consumer
        consumer.stop()
        queue.put(None)
        consumer.join()

        urls = list(set(urls))
        bookQueue = Queue(20)
        producers.clear()

        # create parse item consumer
        consumer = Consumer('Consumer', minNum, maxNum, k, bookQueue, bookInfos)
        consumer.start()

        print(" urls: ", len(urls))
        # create parge item producers
        for url in urls:
            producer = Producer(url, url, bookQueue)
            producer.start()
            producers.append(producer)
            #print(" > process item : {0}".format(url))
            time.sleep(0.2)         # slow down a little

        # wait for all producers
        for producer in producers:
            producer.join()

        # wait for consumer
        consumer.stop()
        queue.put(None)
        consumer.join()

        # summrise
        total = len(bookInfos)
        elapsed = timeit.default_timer() - start
        print("   获取 %d 本我想读的书，耗时 %.2f 秒"%(total, elapsed))
        return bookInfos


def process(wishUrl, minNum, maxNum, k):
    # spider
    books = spider(wishUrl, minNum, maxNum, k)
    if books != None:
        books = list(set(books))

        total = len(books)
        print(" > 共获取 {0} 本我想读的书".format(total))

        # sort
        books = sorted(books)
        # get top 100
        #books = books[0:100]

        # export to markdown
        exportToMarkdown('我想读的书', books, total)

#=============================================================================
# 排序算法
#=============================================================================
def computeCompositeRating(minNum, maxNum, k, num, people):
    people = max(1, min(maxNum, people))
    if people <= minNum:
        people = minNum / 3
    peopleWeight = math.pow(people, k)
    level4 = max(500, maxNum * 1 / 10)
    level5 = max(1000, maxNum * 3 / 10)
    if people < 50:
        return (num * 40 + peopleWeight * 60) / 100.0
    elif people < 100:
        return (num * 50 + peopleWeight * 50) / 100.0
    elif people < 200:
        return (num * 60 + peopleWeight * 40) / 100.0
    elif people < level4:
        return (num * 70 + peopleWeight * 30) / 100.0
    elif people < level5:
        return (num * 80 + peopleWeight * 20) / 100.0
    else:
        return (num * 90 + peopleWeight * 10) / 100.0

#=============================================================================
# 程序入口：抓取指定标签的书籍
#=============================================================================
if __name__ == '__main__': 

    start = timeit.default_timer()

    username = 'kesalin'
    process(username, 30, 3000, 0.25)

    elapsed = timeit.default_timer() - start
    print("== 总耗时 %.2f 秒 =="%(elapsed))