#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://kesalindev.github.io
# Date          : 2016/07/12
# Description   : Douban Reading Analizer. 
# Version       : 1.0.0.0
# Python Version: Python 2.7.3
#

# data format:
#
# (https://book.douban.com/subject/24536403/)[代码的未来 : 代码的未来]
# [日] 松本行弘 / 周自恒 / 人民邮电出版社 / 2013-6 / 79.00元
# 四星 2016-12-11 读过 标签: 编程
# 中文名有点哗众取宠，这是作者在技术的剖析专栏的合集，看看高手对各种技术的见解，可拓宽知识面，增进对各种技术的认识。
# #end#

import os
import re
import string

class BookInfo:
    name = ''
    url = ''
    ratingNums = ''
    readMonth = ''
    tag = ''
    comment = ''

    def __init__(self, name, url, nums, month, tag, comment):
        self.name = name
        self.url = url
        self.ratingNums = nums
        self.readMonth = month
        self.tag = tag
        self.comment = comment


def read_file(path):
    lines = []

    if(os.path.isfile(path)):
        handle = open(path, 'r')
        for line in handle:
            line = line.strip()
            if len(line) > 0:
                lines.append(line)
        handle.close()
    return lines

def is_begin(line):
    return line.startswith('(https:')

def is_end(line):
    return line.startswith('#end#')

def num_to_kanji(num):
    dict = {1 : "一星", 2 : "两星", 3 : "三星", 4 : "四星", 5 : "五星"}
    if num >= 1 and num <= 5:
        return dict[num]
    else:
        print " ** error: invalid rating num {0}".format(num)
        return ""

def kanji_to_num(kanji):
    dict = {"一" : 1, "二" : 2, "两" : 2, "三" : 3, "四" : 4, "五" : 5}
    return dict[kanji]

def get_book_by_rating(books, rating):
    return [book for book in books if book.ratingNums == rating]

def output_rating_num(file, total, rating, books):
    count = len(books)
    if count > 0:
        file.write(' > {0}图书 {1} 本，占比 {2:2.0f}%  \n'.format(num_to_kanji(rating), count, count * 100.0/total))

def output_tags(file, tags):
    items = sorted(tags.items(), key=lambda d: d[1], reverse=True)
    print items

    file.write('### 标签统计:\n')
    for key, value in items:
        file.write(' > {0} {1} 本  \n'.format(key, value))

def output_rating(file, index, rating, books):
    count = len(books)
    if count == 0:
        return index

    file.write('### {0} 图书: {1} 本\n'.format(num_to_kanji(rating), count))

    books.sort(cmp=None, key=lambda x:(x.ratingNums, x.tag), reverse=True)
    for book in books:
        #print '{0} {1} {2}\n'.format(book.name, book.ratingNums, book.tag)
        file.write('#### No.{0:d} {1}\n'.format(index, book.name))
        file.write(' > 图书名称：[{0}]({1})  \n'.format(book.name, book.url))
        file.write(' > 豆瓣链接：[{0}]({1})  \n'.format(book.url, book.url))
        file.write(' > 标签：{0}\t\t评分：{1}    \n'.format(book.tag, num_to_kanji(book.ratingNums)))
        file.write(' > 我的评论：{0}  \n'.format(book.comment))
        file.write('\n')
        index = index + 1
    file.write('\n')
    return index

def analyze_book(books, tags):
    path = "2016doubanreading.md"
    if(os.path.isfile(path)):
        os.remove(path)
    file = open(path, 'a')

    total = len(books)

    file.write('## 2016年阅读统计\n')
    file.write('## 总计阅读 {0} 本\n'.format(total))
    file.write('### 评价统计:\n')

    rating = 5
    rating5 = get_book_by_rating(books, rating)
    output_rating_num(file, total, rating, rating5)

    rating = 4
    rating4 = get_book_by_rating(books, rating)
    output_rating_num(file, total, rating, rating4)

    rating = 3
    rating3 = get_book_by_rating(books, rating)
    output_rating_num(file, total, rating, rating3)

    rating = 2
    rating2 = get_book_by_rating(books, rating)
    output_rating_num(file, total, rating, rating2)

    rating = 1
    rating1 = get_book_by_rating(books, rating)
    output_rating_num(file, total, rating, rating1)

    file.write('\n')

    output_tags(file, tags)

    file.write('\n')

    index = 1
    index = output_rating(file, index, 5, rating5)
    index = output_rating(file, index, 4, rating4)
    index = output_rating(file, index, 3, rating3)
    index = output_rating(file, index, 2, rating2)
    index = output_rating(file, index, 1, rating1)

    file.close()

def process(datapath):
    books = []
    tags = {}

    name = ''
    url = ''
    ratingNums = 0
    readMonth = -1
    tag = ''
    comment = ''

    index = 0
    lines = read_file(datapath)
    for line in lines:
        index = index + 1

        if is_end(line):
            book = BookInfo(name, url, ratingNums, readMonth, tag, comment)
            books.append(book)
            index = 0
            continue

        if is_begin(line):
            index = 1
            name = ''
            url = ''
            ratingNums = 0
            readMonth = -1
            tag = ''
            comment = ''

            pattern = re.compile(r'(\()(.*)(\))(\[)(.*)(\])')
            match = pattern.search(line)
            if match:
                url = match.group(2)
                name = match.group(5)
                #print " >> new book {0}, url: {1}".format(name, url)
            else:
                print " == error: invalid begin line: {0}".format(line)
            continue

        if index == 3:
            pattern = re.compile(r'(.*)(星\s*)(\d{4})(-)(\d{2})(-)(\d{2})(.*)(标签:\s*)(.*)')
            match = pattern.search(line)
            if match:
                ratingNums = kanji_to_num(match.group(1))
                readMonth = int(match.group(5))
                tag = match.group(10)
                for t in tag.split(' '):
                    if t in tags:
                        tags[t] = tags[t] + 1
                    else:
                        tags[t] = 1

                #print " >> rating {0}, month: {1}, tag: {2}".format(ratingNums, readMonth, tag)
            else:
                print " == error: invalid rating line: {0}".format(line)
            continue

        if index == 4:
            comment = line
            continue

        if index > 5:
            print " ** unknown info: {0}".format(line)

    print " >> total {0} books".format(len(books))

    analyze_book(books, tags)

############################################################################################################
datapath = "2016readings.txt"

process(datapath)

