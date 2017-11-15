#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://luozhaohui.github.io
# Date          : 2014/10/18
# Description   : Export CSND blog articles to Markdown files. 
# Version       : 1.0.0.0
# Python Version: Python 2.7.3
#

import re
import os
import sys
import datetime
import time
import traceback
import codecs
import urllib2
from bs4 import BeautifulSoup

# 获取 url 内容
gUseCookie = False
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

def slow_down():
    time.sleep(0.5)         # slow down a little

def log(str):
    if gEnableLog:
        print(str)

        logPath = os.path.join(gOutputDir, 'log.txt');
        newFile = open(logPath, 'a+')
        newFile.write(str + '\n')
        newFile.close()
        
def decodeHtmlSpecialCharacter(htmlStr):
    specChars = {"&ensp;" : "", \
                 "&emsp;" : "", \
                 "&nbsp;" : "", \
                 "&lt;" : "<", \
                 "&gt" : ">", \
                 "&amp;" : "&", \
                 "&quot;" : "\"", \
                 "&copy;" : "®", \
                 "&times;" : "×", \
                 "&divide;" : "÷", \
                 }
    for key in specChars.keys():
        htmlStr = htmlStr.replace(key, specChars[key])
    return htmlStr

def repalceInvalidCharInFilename(filename):
    specChars = {"\\" : "", \
                 "/" : "", \
                 ":" : "", \
                 "*" : "", \
                 "?" : "", \
                 "\"" : "", \
                 "<" : "小于", \
                 ">" : "大于", \
                 "|" : " and ", \
                 "&" :" or ", \
                 }
    for key in specChars.keys():
        filename = filename.replace(key, specChars[key])
    return filename

# process html content to markdown content
def htmlContent2String(contentStr):
    patternImg = re.compile(r'(<img.+?src=")(.+?)(".+ />)')
    patternHref = re.compile(r'(<a.+?href=")(.+?)(".+?>)(.+?)(</a>)')
    patternRemoveHtml = re.compile(r'</?[^>]+>')

    resultContent = patternImg.sub(r'![image_mark](\2)', contentStr)
    resultContent = patternHref.sub(r'[\4](\2)', resultContent)
    resultContent = re.sub(patternRemoveHtml, r'', resultContent)
    resultContent = decodeHtmlSpecialCharacter(resultContent)
    return resultContent

def exportToMarkdown(exportDir, postdate, categories, title, content):
    titleDate = postdate.strftime('%Y-%m-%d')
    contentDate = postdate.strftime('%Y-%m-%d %H:%M:%S %z')
    filename = titleDate + '-' + title
    filename = repalceInvalidCharInFilename(filename)
    filepath = os.path.join(exportDir, filename + '.markdown')
    log(" >> save as " + filepath)

    newFile = open(unicode(filepath, "utf8"), 'w')
    newFile.write('---' + '\n')
    newFile.write('layout: post' + '\n')
    newFile.write('title: \"' + title + '\"\n')
    newFile.write('date: ' + contentDate + '\n')
    newFile.write('comments: true' + '\n')
    newFile.write('categories: [' + categories + ']' + '\n')
    newFile.write('tags: [' + categories + ']' + '\n')
    newFile.write('description: \"' + title + '\"\n')
    newFile.write('keywords: ' + categories + '\n') 
    newFile.write('---' + '\n\n')
    newFile.write(content)
    newFile.write('\n')
    newFile.close()

def download(title, url, output):
    # 下载文章，并保存为 markdown 格式
    log(" >> download: " + url)

    categories = ""
    content = ""
    postDate = datetime.datetime.now()
    
    slow_down();
    page = getHtml(url)
    soup = BeautifulSoup(page)

    manageDocs = soup.find_all("div", "article_manage")
    for managerDoc in manageDocs:
        categoryDoc = managerDoc.find_all("span", "link_categories")
        if len(categoryDoc) > 0:
            categories = categoryDoc[0].a.get_text().encode('UTF-8').strip()
        
        postDateDoc = managerDoc.find_all("span", "link_postdate")
        if len(postDateDoc) > 0:
            postDateStr = postDateDoc[0].string.encode('UTF-8').strip()
            postDate = datetime.datetime.strptime(postDateStr, '%Y-%m-%d %H:%M')

    contentDocs = soup.find_all(id="article_content")
    for contentDoc in contentDocs:
        htmlContent = contentDoc.prettify().encode('UTF-8')
        content = htmlContent2String(htmlContent)

    exportToMarkdown(output, postDate, categories, title, content)

def getPageUrlList(url):
    page = getHtml(url)
    soup = BeautifulSoup(page)

    lastArticleHref = None
    pageListDocs = soup.find_all(id="papelist")
    for pageList in pageListDocs:
        hrefDocs = pageList.find_all("a")
        if len(hrefDocs) > 0:
            lastArticleHrefDoc = hrefDocs[len(hrefDocs) - 1]
            lastArticleHref = lastArticleHrefDoc["href"].encode('UTF-8')

    if lastArticleHref == None:
        return []
    
    print(" > last page href:" + lastArticleHref)
    lastPageIndex = lastArticleHref.rfind("/")
    lastPageNum = int(lastArticleHref[lastPageIndex+1:])
    urlInfo = "http://blog.csdn.net" + lastArticleHref[0:lastPageIndex]

    pageUrlList = []
    for x in xrange(1, lastPageNum + 1):
        pageUrl = urlInfo + "/" + str(x)
        pageUrlList.append(pageUrl)
        log(" > page " + str(x) + ": " + pageUrl)

    log("total pages: " + str(len(pageUrlList)) + "\n")
    return pageUrlList

def getArticleList(url):
    # 获取所有的文章的 url/title
    pageUrlList = getPageUrlList(url)
    
    articleListDocs = []

    strPage = " > parsing page {0}"
    for pageUrl in pageUrlList:
        retryCount = 0
        print(" > parsing page {0}".format(pageUrl))

        slow_down() #访问太快会不响应
        page = getHtml(pageUrl);
        soup = BeautifulSoup(page)
        
        # 获取置顶文章
        topArticleDocs = soup.find_all(id="article_toplist")
        if topArticleDocs != None:
            articleListDocs = articleListDocs + topArticleDocs

        # 获取文章
        articleDocs = soup.find_all(id="article_list")
        if articleDocs != None:
            articleListDocs = articleListDocs + articleDocs

        break
    
    artices = []
    topTile = "[置顶]"
    for articleListDoc in articleListDocs:
        linkDocs = articleListDoc.find_all("span", "link_title")
        for linkDoc in linkDocs:
            #print(linkDoc.prettify().encode('UTF-8'))
            link = linkDoc.a
            url = link["href"].encode('UTF-8')
            title = link.get_text().encode('UTF-8')
            title = title.replace(topTile, '').strip()
            oneHref = "http://blog.csdn.net" + url
            #log("   > title:" + title + ", url:" + oneHref)
            artices.append([oneHref, title])

    log("total articles: " + str(len(artices)) + "\n")
    return artices

def exportBlog(username, output):
    url = "http://blog.csdn.net/" + username
    path = os.path.join(output, username)

    if not os.path.exists(path):
        os.makedirs(path)

    log(" >> user name: " + username)
    log(" >> output dir: " + path)
    log("start export...")

    articleList = getArticleList(url)
    totalNum = len(articleList)

    log("start downloading...")
    currentNum = 0
    for article in articleList:
        currentNum = currentNum + 1
        strPageTemp = "[{0}/{1}] : {2}".format(currentNum, totalNum, article[1])
        log(strPageTemp)

        download(article[1], article[0], path)

        break

#=============================================================================
# 程序入口
#=============================================================================

# set your CSDN username
gUsername = "kesalin"

# set output dir
gOutputDir = "csdn_posts"

gEnableLog = True

if __name__ == '__main__': 
    exportBlog(gUsername, gOutputDir)