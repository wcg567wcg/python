#!/usr/bin/env python
# encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://luozhaohui.github.io
# Date          : 2016/12/24
# Description   : Generate douban reading rawdata for statistics.
# Version       : 1.0.0.0
# Python Version: Python 2.7.3

import os
import re
import string
from bs4 import BeautifulSoup

# 书籍信息类
class BookInfo:
    name = ''
    url = ''
    icon = ''
    publish = ''
    reading = ''
    comment = ''

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

def parse_item_info(year, item, books):
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
            if False == date.startswith(str(year)):
                return
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
    books.append(bookInfo)

def exportToRawdata(year, books):
    if len(books) < 1:
        return

    path = get_raw_data_path(year)
    file = open(path, 'a')

    for book in books:
        info = "({0})[{1}]\n".format(book.url, book.name)
        file.write(info)
        file.write("{0}\n".format(book.publish))
        file.write("{0}\n".format(book.reading))
        file.write("{0}\n".format(book.comment))
        file.write("#end#\n\n")

    file.close()

def parse(readingHtml, year):
    books = []

    fp = open(readingHtml)
    soup = BeautifulSoup(fp, "lxml")

    items = soup.find_all("li", "subject-item")
    for item in items:
        parse_item_info(year, item, books)

    exportToRawdata(year, books)

def get_raw_data_path(year):
    return u'{0}/{0}reading.data'.format(str(year), str(year))

#=============================================================================
# 程序入口
#=============================================================================
CURRENT_YEAR = 2016
htmls = ['reading001.html']

if __name__ == '__main__':
    path = get_raw_data_path(CURRENT_YEAR)
    if (os.path.isfile(path)):
        os.remove(path)

    for html in htmls:
        parse(html, CURRENT_YEAR)