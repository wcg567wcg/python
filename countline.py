#!/usr/bin/env python
#! encoding=utf-8
#
# countline.py
# counting lines of java/python file or java/python files in a dir
#
# Python Version: Python 3.4.3
#

import os
import codecs


def process_file(path):
    total = 0
    if path.endswith('.java') or path.endswith('.py'):
        with codecs.open(path, 'r', 'utf-8') as handle:
            for line in handle.readlines():
                # print(line)
                line = line.lstrip()
                if len(line) > 1:
                    if not line.startswith("//") and not line.startswith("#"):
                        total += 1
        #print("%s has %d lines"%(path, total))
    return total


def process_dir(path):
    total = 0

    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            # exclude hidden dirs
            if filename.startswith("."):
                pass
            else:
                total += process_dir(filepath)
        elif os.path.isfile(filepath):
            total += process_file(filepath)
    return total


def process(path):
    total = 0
    if os.path.isdir(path):
        total = process_dir(path)
    elif os.path.isfile(path):
        total = process_file(path)

    print('>>> total code lines : %d' % total)
    return total

import os
import time
import datetime
from threading import Thread,currentThread,activeCount

date = datetime.datetime.now()
week = date.weekday()

def clean_log():
    print("week: {}".format(week))
    for root, dirs, filenames in os.walk("/home/kesalin/Documents/roslog", topdown=True, onerror=None, followlinks=False):
        for filename in filenames:
            if ".log" in filename and root =="/home/kesalin/Documents/roslog":
                temp_name = filename.split("-")
                length = len(temp_name)

                print("filename: {}".format(filename))
                print("temp_name: {}".format(temp_name))
                print("temp_name length: {}".format(length))

                key_value = -1
                if length >= 3:
                    tmp = temp_name[len(temp_name)-2]
                    print("tmp: {}".format(tmp))
                    try:
                        key_value = int(tmp)
                        print("key_value: {}".format(key_value))
                    except ValueError:
                        print("ValueError: {}".format(filename))
                elif length == 2:
                    tmp = temp_name[len(temp_name)-1]
                    print("tmp: {}".format(tmp))
                    try:
                        key_value = int(tmp.split(".")[0])
                        print("key_value: {}".format(key_value))
                    except ValueError:
                        print("ValueError: {}".format(filename))

                if key_value >= 0 and week+1 != key_value:
                    cmd = "rm -r /home/kesalin/Documents/roslog/" + filename
                    print("excute: {}".format(cmd))
                    os.system(cmd)

# process('countline.py')
# process('matplot')

clean_log()
