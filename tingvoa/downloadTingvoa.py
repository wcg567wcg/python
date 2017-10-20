#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://luozhaohui.github.io
# Date          : 2017/10/20
# Description   : download resources from tingvoa.com 
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

# 
class LevelInfo:
    name = ''
    url = ''
    bookInfos = []

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__( self ):
        return "Level:{0}, url:{1}, books:{2}\n".format(self.name, self.url, len(self.bookInfos))
# 
class BookInfo:
    name = ''
    url = ''
    chapterInfos = []

    def __init__(self, name, url, infos):
        self.name = name
        self.url = url
        self.chapterInfos = infos

    def __str__( self ):
        return "Book:{0}, url:{1}, chapters:[2]".format(self.name, self.url, len(self.chapterInfos))
# 
class ChapterInfo:
    name = ''
    url = ''
    mp3Url = ''

    def __init__(self, name, url, mp3):
        self.name = name
        self.url = url
        self.mp3Url = mp3

    def __str__( self ):
        return "Chapter:{0}, url:{1}, mp3:{2}".format(self.name, self.url, self.mp3Url)

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


def get_root_url(url):
    rootUrl = url
    start = url.find(".")
    if start > 0:
        index = url.find("/", start);
        if index > 0:
            rootUrl = url[0:index]
    return rootUrl

# parse resource url
def parse(url):
    start = timeit.default_timer()

    rootUrl = get_root_url(url)
    print "rootUrl: " + rootUrl

    levelInfos = []

    page = getHtml(url)
    soup = BeautifulSoup(page, 'html.parser')

    # get doulist title
    #pageTitle = soup.html.head.title.string.encode('utf-8')
    #print " > page title：" + pageTitle

    # get resource title
    resourceTitle = ""
    content = soup.find(id="containertow")
    if content != None:
        titleContent = content.find("div", "catmenutitle");
        if titleContent != None and titleContent.string != None:
            resourceTitle = titleContent.string.strip().encode('utf-8')
            #print " > resource title：" + resourceTitle

    # get level infos
    mainleftlist = soup.find(id="mainleftlist");
    if (mainleftlist != None):
        #print mainleftlist.prettify()
        leftTitles = mainleftlist.find_all("div", "leftTitle")
        print "find %d levels" % len(leftTitles)
        for leftTitle in leftTitles:
            #print leftTitle.prettify()
            link = leftTitle.find("a");
            if link != None:
                levelName = ""
                if link.string != None:
                    levelName = link.string.strip().encode('utf-8')
                href = link['href'].encode('utf-8')
                levelUrl = rootUrl + href;

                levelInfo = LevelInfo(levelName, levelUrl)
                levelInfos.append(levelInfo)
                #print levelInfo

    for levelInfo in levelInfos:
        parse_level(levelInfo)

    store_resource(resourceTitle, levelInfos)

def slow_down():
	time.sleep(0.5)         # slow down a little

def parse_level(levelInfo):
    name = levelInfo.name
    url = levelInfo.url
    rootUrl = get_root_url(url)
    #print "rootUrl: " + rootUrl

    slow_down()
    page = getHtml(url)
    soup = BeautifulSoup(page, 'html.parser')

    # get book infos
    mainleftlist = soup.find(id="mainleftlist");
    if (mainleftlist != None):
        #print mainleftlist.prettify()
        leftTitles = mainleftlist.find_all("div", "leftTitle")
        #print "find %d books" % len(leftTitles)
        for leftTitle in leftTitles:
            #print leftTitle.prettify()
            link = leftTitle.find("a");
            if link != None:
                bookName = ""
                if link.string != None:
                    bookName = link.string.strip().encode('utf-8')
                href = link['href'].encode('utf-8')
                bookUrl = rootUrl + href;

                chapterInfos = []
                subleftList = leftTitle.findNext("div")
                if subleftList != None:
                    #print subleftList.prettify()
                    allLinks = subleftList.findAll("a")
                    for link in allLinks[1:]:
                        chapterName = ""
                        if link.string != None:
                            chapterName = link.string.strip().encode('utf-8')
                        href = link['href'].encode('utf-8')
                        chapterUrl = rootUrl + href;
                        mp3Url = parse_chapter(chapterUrl)
                        chapterInfo = ChapterInfo(chapterName, chapterUrl, mp3Url)
                        chapterInfos.append(chapterInfo)
                        #print chapterInfo

                bookInfo = BookInfo(bookName, bookUrl, chapterInfos)
                levelInfo.bookInfos.append(bookInfo)
                #print bookInfo

    #print "parse: %s" % levelInfo

def parse_chapter(chapterUrl):
    rootUrl = get_root_url(chapterUrl)

    slow_down()
    page = getHtml(chapterUrl)
    soup = BeautifulSoup(page, 'html.parser')
    content = soup.prettify().encode('utf-8')

    mp3Url = ""
    #var mp3 ="Sound/shuchong/aqyjq/tingvoa.com_1.mp3";
    pattern = re.compile(r'(var mp3)(\s*)(=)(\s*)(")(.*)(.mp3)(")')
    match = pattern.search(content)
    if match:
        mp3 = "{0}{1}".format(match.group(6), match.group(7))
        mp3Url = "http://x8.tingvoa.com/{1}".format(rootUrl, mp3)
        #print mp3Url
    return mp3Url

def store_resource(title, levelInfos):
    path = "{0}.md".format(title)
    if(os.path.isfile(path)):
        os.remove(path)

    today = datetime.datetime.now()
    todayStr = today.strftime('%Y-%m-%d %H:%M:%S %z')
    file = open(path, 'a')
    file.write('## {0}\n'.format(title))
    file.write('### 总计 {0} levels\n'.format(len(levelInfos)))
    file.write('### update time: {0}\n'.format(todayStr))

    i = 0
    for level in levelInfos:
        file.write('\n### Level.{0:d} {1}\n'.format(i + 1, level.name))

        j = 0
        for book in level.bookInfos:
            file.write('\n#### Book.{0:d} {1}\n'.format(j + 1, book.name))

            k = 0
            for chapter in book.chapterInfos:
                file.write('##### Chapter.{0:d} {1}, {2}\n'.format(k + 1, chapter.name, chapter.mp3Url))
                k = k + 1

            j = j + 1
        i = i + 1
    file.close()

#=============================================================================
# main
#=============================================================================
gResourceUrl = "http://www.tingvoa.com/bookworm/"

if __name__ == '__main__': 
    parse(gResourceUrl)