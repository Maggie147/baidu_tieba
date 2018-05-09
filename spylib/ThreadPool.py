# -*- coding: utf-8 -*-

import Queue
import threading
import sys
import time
import urllib

class MyThread(threading.Thread):
    busy=False
    finishsignal=False
    def __init__(self, workQueue, resultQueue,timeout=1, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.timeout = timeout
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.start()
        self.busy=False
        self.finishsignal=False

    def run(self):#检测workQueue队列中为空
        while True:
            try:
                func, args= self.workQueue.get_nowait()
                self.busy=True
                res = func(args)#执行队列中HandMsg函数处理信息
                self.busy=False
                self.resultQueue.put(res)#把结果写入多resultQue中    
            except Queue.Empty: 
                if self.finishsignal:
                    break
                else:
                    time.sleep(2)
                    continue
    
class ThreadPool:
    def __init__( self, num_of_threads=10):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.threads = []
        self.__createThreadPool( num_of_threads )

    def __createThreadPool( self, num_of_threads ):
        for i in range( num_of_threads ):
            thread = MyThread( self.workQueue, self.resultQueue )
            self.threads.append(thread)

    def wait_for_complete(self):
        self.sendFinishSignal()
        while len(self.threads):
            thread = self.threads.pop()
            if thread.isAlive():
                thread.join()
    
    def add_job( self, func, *args):
        self.workQueue.put( (func,args) )
    def sendFinishSignal(self):
        for th in self.threads:
            th.finishsignal=True
    def getWorkingCount(self):
        count=0
        for th in self.threads:
            if th.isAlive() and th.busy:
                count=count+1
        return count
    def getQueueCount(self):
        return self.workQueue.qsize()
        
def test_job(id, sleep = 0.001 ):
    print id
    html = ""
    try:
        time.sleep(1)
        conn = urllib.urlopen('http://baidu.com/')
        html = conn.read(20)
    except:
        print  sys.exc_info()
    return  html

def test():
    print 'start testing'
    tp = ThreadPool(50)
    for i in range(50):
        
        time.sleep(0.2)
        tp.add_job( test_job, i, i*0.001 )
        #print tp.workQueue.empty()
        print tp.getWorkingCount()
  #  
    tp.wait_for_complete()
    print tp.getWorkingCount()
    print 'ok'
    print 'result Queue\'s length == %d '% tp.resultQueue.qsize()
    while tp.resultQueue.qsize():
        print tp.resultQueue.get()
    print 'end testing'
if __name__ == '__main__':
 test()
