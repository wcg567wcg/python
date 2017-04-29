#!/usr/bin/env python
#! encoding=utf-8
# divideBook2Chapters.py
#
# Python 2.7.6

import os
import sys
import codecs
import re

def get_filepath_without_ext(path):
    filename = path
    index = path.rfind('.');
    if index != -1:
        filename = path[0:index]
    return filename

def process_file(path, new_path):
    if (os.path.isfile(new_path)):
        os.remove(new_path)
    in_file = open(path, 'r')
    out_file = open(new_path, 'a')
    for line in in_file:
        pattern = re.compile(r'(------------)(.*)(\sPage\s)(.*)(------------)')
        match = pattern.search(line)
        if match:
            pass
        else:
            #print line
            out_file.write(line)

    in_file.close()
    out_file.close()

def format_book(path):
    new_path = get_filepath_without_ext(path) + "_good.txt"
    process_file(path, new_path)

def kanji_to_num(kanji):
    dict = {"一" : '1', "二" : '2', "三" : '3', "四" : '4', "五" : '5',
        "六" : '6', "七" : '7', "八" : '8', "九" : '9', "十" : '10',
        "" : '0'}
    return dict[kanji]

def convert_name(name):
    #print name
    # >= 110
    pattern = re.compile(r'(一百)(.*)(十)(.*)')
    match = pattern.match(name)
    if match:
        return "1{0}{1}".format(kanji_to_num(match.group(2)), kanji_to_num(match.group(4)))

    # > 100 && <= 110
    pattern = re.compile(r'(一百零)(.*)')
    match = pattern.match(name)
    if match:
        return "10{0}".format(kanji_to_num(match.group(2)))

    # == 100
    pattern = re.compile(r'一百')
    match = pattern.match(name)
    if match:
        return "100"

    if name == "十":
        return '010'

    if name == "零":
        return '000'

    pattern = re.compile(r'(.*)(十)(.*)')
    match = pattern.match(name)
    if match:
        return "0{0}{1}".format(kanji_to_num(match.group(1)), kanji_to_num(match.group(3)))

    return "00{0}".format(kanji_to_num(name))


def divide_into_chapter(path):
    print path
    dir_path = "{0}/chapters".format(os.path.dirname(path))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    chapter = None
    #with codecs.open(path, 'r', 'utf-8') as f:
    with open(path, 'r') as f:
        for line in f:
            l = line.strip()
            pattern = re.compile(r'(^第)([零一二三四五六七八九十百千]*)(回)')
            match = pattern.match(l.strip())
            if match:
                if chapter:
                    chapter.close()

                name = convert_name(match.group(2))
                chapter_path = "{0}/{1}.txt".format(dir_path, name)
                print chapter_path
                if (os.path.isfile(chapter_path)):
                    os.remove(chapter_path)
                chapter = open(chapter_path, 'a')
                chapter.write(line)
            else:
                #print line.strip()
                if (chapter):
                    chapter.write(line)

        if chapter:
            chapter.close()

#=======================================================================

if __name__ == '__main__':
    path = '/home/luozhaohui/Documents/python/word_frequence/book/水浒传全集.txt'
    divide_into_chapter(path)
