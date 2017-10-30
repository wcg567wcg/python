#!/usr/bin/env python
# encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://luozhaohui.github.io
# Date          : 2016/12/24
# Description   : Generate douban reading rawdata for statistics.
# Version       : 1.0.0.0
# Python Version: Python 2.7.3

import os
import threading
import time
import datetime
import re
import string
import urllib2
from bs4 import BeautifulSoup

# 获取 url 内容
# How to get your cookie?
# Press F12 in Chrome and read cookie of header under network tab.
#
gUseCookie = True
gHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Cookie': 'Put your cookie here. Press F12 in Chrome and read cookie of header under network tab.'
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
            request = urllib2.Request(url, None, gHeaders['User-Agent'])
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

def slow_down():
    time.sleep(0.5)         # slow down a little

# 书籍信息类
class BookInfo:
    def __init__(self, name, url, icon, publish, reading, comment):
        self.name = name
        self.url = url
        self.icon = icon
        self.publish = publish
        self.reading = reading
        self.comment = comment 

def num_to_kanji(num):
    dict = {1 : "一星", 2 : "两星", 3 : "三星", 4 : "四星", 5 : "五星"}
    if num >= 1 and num <= 5:
        return dict[num]
    else:
        print " ** error: invalid rating num {0}".format(num)
        return ""

def parse_item_info(item, yearBookDict):
    # print item.prettify().encode('utf-8')

    # get book name and url
    name = ''
    url = ''
    content = item.find("div", "info")
    if content != None:
        link = content.find("a")
        if link != None:
            url = link.get('href').strip().encode('utf-8')
            name = link.get('title').strip().encode('utf-8')
    #print " > name: {0}".format(name)
    #print " > url: {0}".format(url)

    # get book icon
    image = ''
    content = item.find("div", "pic")
    if content != None:
        link = content.find("img")
        if link != None:
            image = link.get("src").strip().encode('utf-8')
    #print " > image: {0}".format(image)

    # get book publish
    publish = ''
    content = item.find("div", "pub")
    if content != None:
        if content.string != None:
            publish = content.string.strip().encode('utf-8')
    #print " > publish: {0}".format(publish)

    # get book comment
    comment = ''
    content = item.find("p", "comment")
    if content != None:
        if content.string != None:
            comment = content.string.strip().encode('utf-8')
    #print " > comment: {0}".format(comment)

    # get book reading data
    date = ''
    tags = ''
    star = ''
    year = ''
    content = item.find("span", "date")
    if content != None:
        if content.string != None:
            date = content.string.strip().encode('utf-8').replace('\n', '')
            parts = date.split(' ');
            date = ''
            for part in parts:
                if len(part) > 0:
                    date = "{0} {1}".format(date, part)
            date = date.strip()
            pattern = re.compile(r'([0-9]*)(-)([0-9]*)(-)(.*)')
            match = pattern.search(date)
            if match:
                year = match.group(1)
    #print " > date: {0}".format(date)

    content = item.find("span", "tags")
    if content != None:
        if content.string != None:
            tags = content.string.strip().encode('utf-8')
    #print " > tags: {0}".format(tags)

        p = content.parent
        for child in p.find_all("span"):
            cls = child.get("class")
            if cls != None and len(cls) > 0:
                clsStr = cls[0].strip().encode('utf-8')
                pattern = re.compile(r'(rating)([0-9])(.*)')
                match = pattern.search(clsStr)
                if match:
                    star = num_to_kanji(int(match.group(2)))
                    break

    reading = "{0} {1} {2}".format(star, date, tags)
    #print reading

    # add book info to list
    bookInfo = BookInfo(name, url, image, publish, reading, comment)
    if yearBookDict.has_key(year):
        books = yearBookDict[year]
        contains = [book for book in books if book.url == url]
        if len(contains) == 0:
            books.append(bookInfo)
    else:
        books = [bookInfo]
        yearBookDict[year] = books

def exportToRawdata(yearBookDict):
    if len(yearBookDict) < 1:
        return

    for (year, books) in yearBookDict.items():
        create_directory_if_not_exists(year)
        path = get_raw_data_path(year)
        if os.path.isfile(path):
            os.remove(path)

        print "export {0} books to {1}".format(len(books), path)
        file = open(path, 'w')

        for book in books:
            info = "({0})[{1}]\n".format(book.url, book.name)
            file.write(info)
            file.write("{0}\n".format(book.publish))
            file.write("{0}\n".format(book.reading))
            file.write("{0}\n".format(book.comment))
            file.write("#end#\n\n")

        file.close()

def get_raw_data_path(year):
    return u'{0}/{0}reading.data'.format(str(year), str(year))

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def parse_page(url, yearBookDict):
    try:
        slow_down()
        page = getHtml(url)
        soup = BeautifulSoup(page, "lxml")

        items = soup.find_all("li", "subject-item")
        for item in items:
            parse_item_info(item, yearBookDict)
    except Exception as e:
        print "failed to parse page : {0}".format(url)
        print e

def parse_pages(entry_url):
    page = getHtml(entry_url)
    soup = BeautifulSoup(page, 'html.parser')

    urls = []
    paginator = soup.find('div', 'paginator')
    if paginator != None:
        next = paginator.find('span', 'next')
        if next == None:
            urls.append(entry_url)
            return urls

        pageStep = 0
        lastPageStart = 0
        p1 = ''
        p2 = ''
        p4 = ''
        nextLink = next.find('a')
        if nextLink != None:
            href = nextLink['href'].encode('utf-8')
            pattern = re.compile(r'(.*)(start=)([0-9]+)(.*)')
            match = pattern.search(href)
            if match:
                p1 = match.group(1)
                p2 = match.group(2)
                p4 = match.group(4)
                pageStep = int(match.group(3))

        links = paginator.find_all('a');
        for link in links:
            href = link['href'].encode('utf-8')
            pattern = re.compile(r'(.*)(start=)([0-9]+)(.*)')
            match = pattern.search(href)
            if match:
                start = int(match.group(3))
                if start > lastPageStart:
                    lastPageStart = start

        print "last page starts at %d, page step %d" % (lastPageStart, pageStep)
        for i in range(0, lastPageStart + 1, pageStep):
            url = '{0}{1}{2}{3}'.format(p1, p2, i, p4)
            #print " page start at %d : %s" % (i, url)
            urls.append(url)

    print 'total %d pages' % len(urls)
    return urls

#=============================================================================
# 程序入口
#=============================================================================

entry_url = 'https://book.douban.com/people/kesalin/collect'

if __name__ == '__main__':
    pageUrls = parse_pages(entry_url)
    
    yearBookDict = {}
    for url in pageUrls:
        parse_page(url, yearBookDict)

    # export
    exportToRawdata(yearBookDict)