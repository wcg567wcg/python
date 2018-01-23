#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://kesalin.github.io
# Date          : 2016/07/13
# Description   : 将豆列导出为 Markdown 文件，多线程版本.
# Version       : 1.0.0.0
# Python Version: Python 2.7.3
#

import os
import math
import time
import timeit
import datetime
import re
import string
import urllib2

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
    try:
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
    except urllib2.URLError as e:
        if hasattr(e, "code"):
            print("The server couldn't fulfill the request: " + url)
            print("Error code: %s" % e.code)
        elif hasattr(e, "reason"):
            print("We failed to reach a server. Please check your url: " +
                  url + ", and read the Reason.")
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
        self.compositeRating = 0.0

    def __sortByRating(self, other):
        val = self.ratingNum - other.ratingNum
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

    def getCompositeRating(self):
        if self.compositeRating == 0.0:
            k = 0.15
            people = max(5, min(1000, self.ratingPeople))
            peopleWeight = math.pow(people, k)
            if people < 50:
                self.compositeRating = (
                    self.ratingNum * 80 + peopleWeight * 20) / 100.0
            elif people < 1000:
                self.compositeRating = (
                    self.ratingNum * 90 + peopleWeight * 10) / 100.0
            else:
                self.compositeRating = (
                    self.ratingNum * 95 + peopleWeight * 5) / 100.0

        return self.compositeRating

    def __sortByCompositeRating(self, other):
        val = self.getCompositeRating() - other.getCompositeRating()
        if val < 0:
            return 1
        elif val > 0:
            return -1
        else:
            return 0

    def __cmp__(self, other):
        return self.__sortByCompositeRating(other)


# 导出为 Markdown 格式文件
def exportToMarkdown(doulistTile, doulistAbout, bookInfos):
    path = "{0}.md".format(doulistTile)
    if(os.path.isfile(path)):
        os.remove(path)

    today = datetime.datetime.now()
    todayStr = today.strftime('%Y-%m-%d %H:%M:%S %z')
    file = open(path, 'a')
    file.write('## {0}\n'.format(doulistTile))
    file.write('{0}\n'.format(doulistAbout))
    file.write('## 图书列表\n')
    file.write('### 总计 {0} 本，更新时间：{1}\n'.format(len(bookInfos), todayStr))
    i = 0
    for book in bookInfos:
        file.write('\n### No.{0:d} {1}\n'.format(i + 1, book.name))
        file.write(' > **图书名称**： [{0}]({1})  \n'.format(book.name, book.url))
        file.write(' > **豆瓣链接**： [{0}]({1})  \n'.format(book.url, book.url))
        file.write(' > **豆瓣评分**： {0}  \n'.format(book.ratingNum))
        file.write(' > **评分人数**： {0} 人  \n'.format(book.ratingPeople))
        file.write(' > **我的评论**： {0}  \n'.format(book.comment))
        i = i + 1
    file.close()


# 解析图书信息
def parseItemInfo(page, bookInfos):
    soup = BeautifulSoup(page, 'html.parser')
    items = soup.find_all("div", "doulist-item")
    for item in items:
        # print(item.prettify().encode('utf-8'))

        # get book name
        bookName = ''
        content = item.find("div", "title")
        if content:
            href = content.find("a")
            if href and href.string:
                bookName = href.string.strip().encode('utf-8')
        #print(" > name: {0}".format(bookName))

        # get book url and icon
        bookUrl = ''
        bookImage = ''
        content = item.find("div", "post")
        if content:
            tag = content.find('a')
            if tag:
                bookUrl = tag['href'].encode('utf-8')
            tag = content.find('img')
            if tag:
                bookImage = tag['src'].encode('utf-8')
        #print(" > url: {0}, image: {1}".format(bookUrl, bookImage))

        # get rating
        ratingNum = 0.0
        ratingPeople = 0
        contents = item.find("div", "rating")
        for content in contents:
            if content.name and content.string:
                if content.get("class"):
                    ratingStr = content.string.strip().encode('utf-8')
                    if len(ratingStr) > 0:
                        ratingNum = float(ratingStr)
                else:
                    ratingStr = content.string.strip().encode('utf-8')
                    pattern = re.compile(r'(\()([0-9]*)(.*)(\))')
                    match = pattern.search(ratingStr)
                    if match:
                        ratingStr = match.group(2).strip()
                        if len(ratingStr) > 0:
                            ratingPeople = int(ratingStr)
        #print(" > ratingNum: {0}, ratingPeople: {1}".format(ratingNum, ratingPeople))

        # get comment
        comment = ''
        content = item.find("blockquote", "comment")
        if content:
            for child in content.contents:
                if not child.name and child.string:
                    comment = child.string.strip().encode('utf-8')
        #print(" > comment: {0}".format(comment))

        # add book info to list
        bookInfo = BookInfo(bookName, bookUrl, bookImage,
                            ratingNum, ratingPeople, comment)
        bookInfos.append(bookInfo)


#=============================================================================
# 生产者-消费者模型
#=============================================================================
gQueue = Queue(20)
gBookInfos = []


class Producer(Thread):
    url = ''

    def __init__(self, t_name, url):
        Thread.__init__(self, name=t_name)
        self.url = url

    def run(self):
        global gQueue

        page = getHtml(self.url)
        if page:
            gQueue.put(page)


class Consumer(Thread):
    running = True

    def __init__(self, t_name):
        Thread.__init__(self, name=t_name)

    def stop(self):
        self.running = False

    def run(self):
        global gQueue
        global gBookInfos

        while True:
            if not self.running and gQueue.empty():
                break

            page = gQueue.get()
            if page:
                parseItemInfo(page, gBookInfos)
            gQueue.task_done()


# 解析豆列 url
def parse(url):
    start = timeit.default_timer()

    # all producers
    producers = []

    # get first page of doulist
    page = getHtml(gDoulistUrl)

    # get url of other pages in doulist
    soup = BeautifulSoup(page, 'html.parser')

    # get doulist title
    doulistTile = soup.html.head.title.string.encode('utf-8')
    print(" > 获取豆列：" + doulistTile)

    # get doulist about
    doulistAbout = ''
    content = soup.find("div", "doulist-about")
    for child in content.children:
        if child.string:
            htmlContent = child.string.strip().encode('utf-8')
            doulistAbout = "{0}\n{1}".format(doulistAbout, htmlContent)
    #print("doulist about:" + doulistAbout)

    nextPageStart = 100000
    lastPageStart = 0
    content = soup.find("div", "paginator")
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

    # create consumer
    consumer = Consumer('Consumer')
    consumer.start()

    # get books from current page
    gQueue.put(page)

    # get books from follow pages
    for pageStart in range(nextPageStart, lastPageStart + nextPageStart, nextPageStart):
        pageUrl = "{0}?start={1:d}&sort=seq&sub_type=".format(url, pageStart)
        print(' > process page :  {0}'.format(pageUrl))
        producer = Producer('Producer_{0:d}'.format(pageStart), pageUrl)
        producer.start()
        producers.append(producer)

    # wait for all producers
    for producer in producers:
        producer.join()

    # wait for consumer
    consumer.stop()
    gQueue.put(None)
    consumer.join()

    # sort
    books = sorted(gBookInfos)

    # export to markdown
    exportToMarkdown(doulistTile, doulistAbout, books)

    # summrise
    total = len(books)
    elapsed = timeit.default_timer() - start
    print(" > 共获取 {0} 本图书信息，耗时 {1} 秒".format(total, elapsed))

#=============================================================================
# 程序入口：解析指定豆列
#=============================================================================
gDoulistUrl = "https://www.douban.com/doulist/1133232/"

if __name__ == '__main__':
    parse(gDoulistUrl)
