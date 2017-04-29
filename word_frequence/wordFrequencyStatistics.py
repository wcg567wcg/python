#!/usr/bin/env python
#! encoding=utf-8
# wordFrequencyStatistics.py
#
# Python 2.7.6
# install libs
# sudo apt-get install python-setuptools
# sudo easy_install jieba

import jieba
from collections import Counter
import codecs
import os
import sys
import re
import string


reload(sys)
sys.setdefaultencoding("utf-8")

enable_log = False

def get_filename_without_ext(path):
    filename = os.path.basename(path)
    index = filename.rfind('.');
    if index != -1:
        filename = filename[0:index]
    return filename

def save_to_file(list, path):
    if (os.path.isfile(path)):
        os.remove(path)
    print "> saving to {0}".format(path)
    with open(path, 'a') as f:
        for item in list:
            f.write('{0} : {1}\n'.format(item[0].encode('utf-8'), item[1]))

def log_dict(info, dict):
    if enable_log:
        if info != '':
            print info
        for (letter, count) in  dict.items():
            print '%s\t\t: %d' % (letter, count)
        print "\n"

def log_list(info, list):
    if enable_log:
        if info != '':
            print info
        for item in list:
            print '%s\t\t: %d' % (item[0], item[1])
        print "\n"

def remove_punctuation(document):
    document = str(document)

    # 去除英文标点&回车&空点
    document = document.translate(None, string.punctuation + '\n ')
    # 去除中文标点
    regex = re.compile(ur"[^\u4e00-\u9fa5a-zA-Z0-9\s]")
    return regex.sub('', document.decode('utf-8'))

def read(path):
    raw_dict = Counter()
    with codecs.open(path, 'r', 'utf-8') as f:
        document = ""
        for line in f:
            line = line.rstrip().lower()
            document += line

        document = remove_punctuation(document)
        seg_list = jieba.cut(document, cut_all=False)
        raw_dict.update(seg_list)

    log_dict('Raw items:', raw_dict)

    # # most common items
    # print '\nMost common items:'
    # for letter, count in raw_dict.most_common(3):
    #     print '%s\t\t: %d' % (letter, count)
    return raw_dict

def filter(dict, keys, min_limit):
    filter_dict = {
        key : dict[key]
        for key in dict.keys()
        if (key not in filter_keys) and dict[key] >= max(count_min_limit, 1)
    }

    log_dict('Filtered items:', filter_dict)
    return filter_dict

def sort(dict):
    sorted_list = sorted(dict.iteritems(), key=lambda d:d[1], reverse = True)
    log_list('Sorted items:', sorted_list)
    return sorted_list

def top(list, num):
    if num <= 0:
        return list

    top_list = list[0 : min(len(list), num)]
    if enable_log:
        print 'Toppest %d items:' % num
    log_list('', top_list)
    return top_list

def process_file(path, data_path, num_top, filter_keys, count_min_limit):
    if path.endswith('_wordfrq.txt'):
        return

    print ">> processing %s ..." % path
    counter_dict = read(path)
    filter_dict = filter(counter_dict, filter_keys, count_min_limit)
    sorted_list = sort(filter_dict)
    top_list = top(sorted_list, num_top)

    # new_path = "{0}/data/".format(os.path.dirname(path))
    new_path = data_path
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    basename = get_filename_without_ext(path)
    new_path = "{0}{1}_wordfrq.txt".format(new_path, basename)
    save_to_file(top_list, new_path)

def process_dir(path, data_path, num_top, filter_keys, count_min_limit):
    if path.endswith('/'):
        path = path[0:len(path)-1]

    print ">>> processing directory %s ..." % path
    listfile = os.listdir(path)
    for filename in listfile:
        filepath = path + '/' + filename
        if (os.path.isdir(filepath)):
            # exclude hidden dirs
            if (filename[0] != '.'):
                process_dir(filepath, data_path, num_top, filter_keys, count_min_limit)
        elif(os.path.isfile(filepath)):
            process_file(filepath, data_path, num_top, filter_keys, count_min_limit)

def word_frequency_statistics(path, data_path, num_top, filter_keys, count_min_limit):
    if (os.path.isdir(path)):
        process_dir(path, data_path, num_top, filter_keys, count_min_limit)
    elif (os.path.isfile(path)):
        process_file(path, data_path, num_top, filter_keys, count_min_limit)

#====================================================================
path = '/home/luozhaohui/Documents/python/word_frequence/book/'
data_path = '/home/luozhaohui/Documents/python/word_frequence/book/data/'

filter_keys = [u'\n', u' ']
count_min_limit = 1
num_top = -1   # -1 means all

if __name__ == '__main__':
    word_frequency_statistics(path, data_path, num_top, filter_keys, count_min_limit)
