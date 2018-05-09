# -*- encoding: utf-8-*-
'''
Created on 2013-11-13

@author: root
'''
import sys 
import random
from threading import Thread
import Queue
import socket
import sysTool
import os
class IPCModule():
    IPCMsgQueue=None
    sock=None
    Enable=True
    IPCType=""
    IPCName_s=""
    IPCName_c=""
    ThreadHandle=None
    AutoExit4C=False
    def __init__(self,IPCType,IPCName,AutoExit4C=False):
        self.IPCMsgQueue=Queue.Queue()
        self.IPCName_s=IPCName+'s'
        print "the self.IPCName_s is:",self.IPCName_s        
        self.IPCName_c=IPCName+'-'+str(random.random())
        print "the self.IPCName_c is:",self.IPCName_c     
        self.IPCType=IPCType
        print "the self.IPCType is:",self.IPCType
        self.AutoExit4C=AutoExit4C
        self.__StartIPC()
        try:
            self.ThreadHandle=Thread(target=self._RecvThread)
            self.ThreadHandle.setDaemon(True)       
            self.ThreadHandle.start()
        except Exception,e: 
            sysTool.DEBUG("_RecvThread error:%d,%s"%(e.args[0],e.args[1]))
    def __StartIPC(self):
        os.system('rm %s -rf'%(self.IPCName_c[0:self.IPCName_c.find('-')+1]+'*'))
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.AF_UNIX,socket.SO_REUSEADDR,1)
        if self.IPCType=="S" or self.IPCType=="s":
            if os.path.exists(self.IPCName_s):
                os.unlink(self.IPCName_s)
            self.sock.bind(self.IPCName_s)
        elif self.IPCType=="C" or self.IPCType=="c":
            if os.path.exists(self.IPCName_c):
                os.unlink(self.IPCName_c)
            self.sock.bind(self.IPCName_c) 
        else:
            sysTool.DEBUG("Invalid IPC server type [%s],abort!"%self.IPCType)
    def WaitIPC(self):
        try:
            self.ThreadHandle.join(5000)
        except KeyboardInterrupt:
            print "User press Ctrl+C,exit!"
            self.StopIPC()
    def StopIPC(self):
        self.Enable=False
        self.sock.close();
        if self.IPCType=="S" or self.IPCType=="s":
            if os.path.exists(self.IPCName_s):
                os.unlink(self.IPCName_s)
        elif self.IPCType=="C" or self.IPCType=="c":
            if os.path.exists(self.IPCName_c):
                os.unlink(self.IPCName_c)
    def SendMsg(self,msg,addrTo=None):
        #print 'a'
        try:
            if self.IPCType=='s' or self.IPCType=='S':
                self.sock.sendto(msg,addrTo)
            else:
                self.sock.sendto(msg,self.IPCName_s)
	    #print 'b'
        except Exception,e:
            #print e
            #print 'c'	    
#            sysTool.DEBUG("Send IPC msg error:%d,%s"%(e[0],e[1])) 
#            self.StopIPC()
            return False
#        if self.IPCType=="C" or self.IPCType=="c":
#            if os.path.exists(self.IPCName_c):
#                os.unlink('/tmp/'+self.IPCName_c)
        return True
    def _RecvThread(self):
        while self.Enable:
            data=self.RecvMsg()
            #print data[0]
            self.IPCMsgQueue.put(data)
            if self.IPCType=='c' or self.IPCType=='C' and self.AutoExit4C:
                self.StopIPC()
                break
    def RecvMsg(self):
        return self.sock.recvfrom(65500)
