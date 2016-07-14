#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://kesalin.github.io
# Date          : 2016/07/12
# Description   : 将豆列导出为 Markdown 文件. 
# Version       : 1.0.0.0
# Python Version: Python 2.7.3
#

import os
import threading
import time
import datetime
import re
import string
import urllib2
import timeit
from bs4 import BeautifulSoup

gHeader = {"User-Agent": "Mozilla-Firefox5.0"}

# 书籍信息类
class BookInfo:
    name = ''
    url = ''
    icon = ''
    ratingNum = 0.0
    ratingPeople = 0
    comment = ''

    def __init__(self, name, url, icon, nums, people, comment):
        self.name = name
        self.url = url
        self.icon = icon
        self.ratingNum = nums
        self.ratingPeople = people
        self.comment = comment 

# 获取 url 内容
def getHtml(url):
    try :
        request = urllib2.Request(url, None, gHeader)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
    except urllib2.URLError, e :
        if hasattr(e, "code"):
            print "The server couldn't fulfill the request: " + url
            print "Error code: %s" % e.code
        elif hasattr(e, "reason"):
            print "We failed to reach a server. Please check your url: " + url + ", and read the Reason."
            print "Reason: %s" % e.reason
    return data

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
        file.write(' > **评分人数**： {0} 人 \n'.format(book.ratingPeople))
        file.write(' > **我的评论**： {0}  \n'.format(book.comment))
        i = i + 1
    file.close()

# 解析图书信息
def parseItemInfo(page, bookInfos):
    soup = BeautifulSoup(page, 'html.parser')
    items = soup.find_all("div", "doulist-item")
    for item in items:
        #print item.prettify().encode('utf-8')

        # get book name
        bookName = ''
        content = item.find("div", "title")
        if content != None:
            href = content.find("a")
            if href != None and href.string != None:
                bookName = href.string.strip().encode('utf-8')
        #print " > name: {0}".format(bookName)

        # get book url and icon
        bookUrl = ''
        bookImage = ''
        content = item.find("div", "post")
        if content != None:
            tag = content.find('a')
            if tag != None:
                bookUrl = tag['href'].encode('utf-8')
            tag = content.find('img')
            if tag != None:
                bookImage = tag['src'].encode('utf-8')
        #print " > url: {0}, image: {1}".format(bookUrl, bookImage)


        # get rating
        ratingNum = 0.0
        ratingPeople = 0
        contents = item.find("div", "rating")
        for content in contents:
            if content.name != None and content.string != None:
                if content.get("class") != None:
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
        #print " > ratingNum: {0}, ratingPeople: {1}".format(ratingNum, ratingPeople)

        # get comment
        comment = ''
        content = item.find("blockquote", "comment")
        if content != None:
            for child in content.contents:
                if child.name == None and child.string != None:
                    comment = child.string.strip().encode('utf-8')
        #print " > comment: {0}".format(comment)

        # add book info to list
        bookInfo = BookInfo(bookName, bookUrl, bookImage, ratingNum, ratingPeople, comment)
        bookInfos.append(bookInfo)

# 解析豆列 url
def parse(url):
    start = timeit.default_timer()

    page = getHtml(url)
    soup = BeautifulSoup(page, 'html.parser')

    # get doulist title
    doulistTile = soup.html.head.title.string.encode('utf-8')
    print " > 获取豆列：" + doulistTile

    # get doulist about
    doulistAbout = ''
    content = soup.find("div", "doulist-about")
    for child in content.children:
        if child.string != None:
            htmlContent = child.string.strip().encode('utf-8')
            doulistAbout = "{0}\n{1}".format(doulistAbout, htmlContent)
    #print "doulist about:" + doulistAbout


    # get page urls
    pageUrls = []

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

    books = []

    # get books from current page
    print ' > process page: {0}'.format(url)
    parseItemInfo(page, books)

    # get books from follow pages
    for pageStart in range(nextPageStart, lastPageStart + nextPageStart, nextPageStart):
        pageUrl = "{0}?start={1:d}&sort=seq&sub_type=".format(url, pageStart)
        print ' > process page: {0}'.format(pageUrl)
        page = getHtml(pageUrl)
        if page != None:
            parseItemInfo(page, books)

    # export to markdown file
    exportToMarkdown(doulistTile, doulistAbout, books)

    # summrise
    total = len(books)
    elapsed = timeit.default_timer() - start
    print " > 共获取 {0} 本图书信息，耗时 {1} 秒".format(total, elapsed)

#=============================================================================
# 程序入口：抓取指定指定豆列的书籍
#=============================================================================
gDoulistUrl = "https://www.douban.com/doulist/1133232/"

if __name__ == '__main__': 
    parse(gDoulistUrl)
