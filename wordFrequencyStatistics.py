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

enable_log = True

def get_filepath_without_ext(path):
    filename = path
    index = path.rfind('.');
    if index != -1:
        filename = path[0:index]
    return filename

def save_to_file(list, path):
    if (os.path.isfile(path)):
        os.remove(path)
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

def read(path):
    raw_dict = Counter()
    with codecs.open(path, 'r', 'utf-8') as f:
        for line in f:
            line = line.rstrip().lower()
            seg_list = jieba.cut(line, cut_all=False)
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
        if (key not in filter_keys) and dict[key] >= count_min_limit
    }

    log_dict('Filtered items:', filter_dict)
    return filter_dict

def sort(dict):
    sorted_list = sorted(dict.iteritems(), key=lambda d:d[1], reverse = True)
    log_list('Sorted items:', sorted_list)
    return sorted_list

def top(list, num):
    top_list = list[0 : num_top]
    print 'Toppest %d items:' % num_top
    log_list('', top_list)
    return top_list

def process_file(path, num_top, filter_keys, count_min_limit):
    if path.endswith('_fenci.txt'):
        return

    print ">> processing %s ..." % path
    counter_dict = read(path)
    filter_dict = filter(counter_dict, filter_keys, count_min_limit)
    sorted_list = sort(filter_dict)
    top_list = top(sorted_list, num_top)

    new_path = get_filepath_without_ext(path) + "_fenci.txt"
    save_to_file(top_list, new_path)

def process_dir(path, num_top, filter_keys, count_min_limit):
    if path.endswith('/'):
        path = path[0:len(path)-1]

    print ">>> processing directory %s ..." % path
    listfile = os.listdir(path)
    for filename in listfile:
        filepath = path + '/' + filename
        if (os.path.isdir(filepath)):
            # exclude hidden dirs
            if (filename[0] != '.'):
                process_dir(filepath, num_top, filter_keys, count_min_limit)
        elif(os.path.isfile(filepath)):
            process_file(filepath, num_top, filter_keys, count_min_limit)

def word_frequency_statistics(path, num_top, filter_keys, count_min_limit):
    if (os.path.isdir(path)):
        process_dir(path, num_top, filter_keys, count_min_limit)
    elif (os.path.isfile(path)):
        process_file(path, num_top, filter_keys, count_min_limit)

#====================================================================
path = '/home/luozhaohui/Documents/python/fenci/data/'
filter_keys = [u'，', u'。', u'、', u'!', u'；']
count_min_limit = 2
num_top = 2

if __name__ == '__main__':
    word_frequency_statistics(path, num_top, filter_keys, count_min_limit)
