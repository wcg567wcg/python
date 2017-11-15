#!/usr/bin/env python
#! encoding=utf-8
#
# countline.py
# counting lines of java/python file or java/python files in a dir
#
# Python Version: Python 3.4.3
#

import os
import sys
import codecs

def process_file(path):
    total = 0
    if path.endswith('.java') or path.endswith('.py'):
        with codecs.open(path, 'r', 'utf-8') as handle:
            for line in handle.readlines():
                #print(line)
                line = line.lstrip()
                if len(line) > 1:
                    if line.startswith("//") == False and line.startswith("#") == False:
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

process('countline.py')
#process('matplot')
