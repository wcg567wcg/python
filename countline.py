#!/usr/bin/env python
#! encoding=utf-8

# countline.py
# counting lines of java file or java files in a dir

import os
import sys
import codecs

def process_file(path):
    total = 0
    if (path.endswith('.java') or path.endswith('.py')):
        handle = codecs.open(path, 'r', 'utf-8')
        for eachLine in handle:
            print(eachLine)
            eachLine = eachLine.lstrip()
            if len(eachLine) > 1:
                if (eachLine.startswith("//") == False):
                    total += 1
        handle.close()
        #print("%s has %d lines"%(path, total))
    return total

def process_dir(path):
    total = 0
    listfile = os.listdir(path)
    for filename in listfile:
        filepath = path + '/' + filename
        if(os.path.isdir(filepath)):
            # exclude hidden dirs
            if(filename[0] == '.'):
                pass
            else:
                total += process_dir(filepath)
        elif(os.path.isfile(filepath)):
            total += process_file(filepath)
    return total

def process(path):
    total = 0
    if(os.path.isdir(path)):
        total = process_dir(path)
    elif(os.path.isfile(path)):
        total = process_file(path)

    print('>>> total lines : %d'%total)
    return total

process('/home/luozhaohui/test.py')
#process('/home/kesalin/test/Settings')
