#!/usr/bin/env python
#! encoding=utf-8

# Author        : kesalin@gmail.com
# Blog          : http://kesalin.github.io
# Date          : 2016/07/26
# Description   : Producer-Consumer
# Version       : 1.0.0.0
# Python Version: Python 2.7.3

from threading import Thread, Condition
import time
import random
 
queue = []
MAX_NUM = 5
condition = Condition()
 
class ProducerThread(Thread):
    isExit = False

    def run(self):
        nums = range(MAX_NUM)
        global queue
        while self.isExit == False:
            condition.acquire()
            if len(queue) == MAX_NUM:
                print "Queue full, producer is waiting"
                condition.wait()
                print "Space in queue, Consumer notified the producer"
            num = random.choice(nums)
            queue.append(num)
            print "Produced", num

            condition.notify()
            condition.release()
            time.sleep(random.random())

    def end(self):
        self.isExit = True

class ConsumerThread(Thread):
    isExit = False

    def run(self):
        global queue
        while self.isExit == False:
            condition.acquire()
            if not queue:
                print "Nothing in queue, consumer is waiting"
                condition.wait()
                print "Producer added something to queue and notified the consumer"
            num = queue.pop(0)
            print "Consumed", num

            condition.notify()
            condition.release()
            time.sleep(random.random())

    def end(self):
        self.isExit = True

p = ProducerThread();
c = ConsumerThread()

p.start()
c.start()

time.sleep(5)

p.end()
c.end()

