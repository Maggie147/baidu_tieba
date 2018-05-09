# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import pprint
import cPickle as pickle
from xml.etree import ElementTree
from pymongo import MongoClient
import pymongo, traceback


class MongoConnector(object):
    def __init__(self):
        pwd = os.path.dirname(os.path.realpath(__file__))
        dirs = pwd.split('/')
        conffile = os.path.join('/home', dirs[2], 'conf/SysSet.xml')
        # conffile = '/home/SecDR_F118X/conf/SysSet.xml'
        tree = ElementTree.ElementTree(file = conffile)#读取XML配置文件获取数据库有关的信息
        root = tree.getroot()
        node = root.find('database')

        if node is None:
            print 'There is no a node named database in the conf file: %s' % (conffile)
            sys.exit(1)
        ip = node.find('db_address')
        if ip is None:
            print 'There is no a node named db_address in the conf file: %s' % (conffile)
            sys.exit(1)
        port = node.find('db_port')
        if port is None:
            print 'There is no a node named db_port in the conf file: %s' % (conffile)
            sys.exit(1)
        db = node.find('db_name')
        if db is None:
            print 'There is no a node named db_name in the conf file: %s' % (conffile)
            sys.exit(1)
        user = node.find('db_user')
        if user is None:
            print 'There is no a node named db_user in the conf file: %s' % (conffile)
            sys.exit(1)
        pwd = node.find('db_pwd')
        if pwd is None:
            print 'There is no a node named db_pwd in the conf file: %s' % (conffile)
            sys.exit(1)

        uri = 'mongodb://%s:%s@%s:%s/%s' % (user.text, pwd.text, ip.text, port.text, db.text)
        print uri
        self.__client = None
        self.__db = None
        try:
            self.__client = MongoClient(host = uri)#链接数据库
            self.__db = self.__client[db.text]
        except pymongo.errors.PyMongoError, e:
            print str(e)
            sys.exit(1)

    '''
    插入mon数据库
    info：插入的信息
    collection_name:要插入的数据所在的表名
    '''
    def insert(self,info,collection_name):
        try:
            QQtable = self.__db[collection_name]
            QQtable.insert(info)
        except pymongo.errors.PyMongoError, e:
            print str(e)
            sys.exit(1)

    def insert_many(self,info,collection_name):
        results = None
        try:
            QQtable = self.__db[collection_name]
            results = QQtable.insert_many(info, False)
        except pymongo.errors.PyMongoError, e:
            print str(e)
            sys.exit(1)
        finally:
            return results

    '''
    查找mongo数据库是否存在对应的值
    info：要查找的数据
    collection_name:查找的数据库的表名
    '''
    def find(self,info,collection_name):
        cursor = {}
        try:
            collection = self.__db[collection_name]
            cursor = collection.find_one(info)
        except pymongo.errors.PyMongoError, e:
            print str(e)
        finally:
            #print '>>>>>>',type(cursor)
            return cursor

    def findall(self, collection_name, query = None, field = None, sort = None, limit = 0):
        cursor = {}
        try:
            collection = self.__db[collection_name]
            cursor = collection.find(query, field, sort = sort, limit = limit)
        except Exception, e:
            print traceback.print_exc()
        finally:
            return cursor


    '''
    更新mongo数据库中对应的值
    info：要更改的数据
    value：更改过后的数据
    collection_name:更新的数据库的表名
    '''
    def update(self,info,value,collection_name):
        try:
            collection = self.__db[collection_name]
            collection.update_one(info,value,True)
        except pymongo.errors.PyMongoError, e:
            print str(e)
            sys.exit(1)

    def export(self, collection_name):
        try:
            collection = self.__db[collection_name]
            collection.find()
        except pymongo.errors.PyMongoError,e:
            print str(e)

    def drop(self, collection_name):
        try:
            collection = self.__db[collection_name]
            collection.drop()
        except pymongo.errors.PyMongoError,e:
            print str(e)

def test():
    info = {'QQ':'123456789','updateTime':'987654321','flag':'1'}
    info1 = {'QQ':1092354}
    info2 ={'$set':{'QQ':789645321,'updateTime':444444444}}
    result = {}
    aa = MongoConnector()
    # startTime = int(time.time())
    # for i in range(500,700):
    #     info = {'QQ':i,'updateTime':int(time.time())}
    #     aa.insert(info,'bbbb')

    # endTime = int(time.time())
    # print endTime-startTime
    # print 'end insert >>>>>>>>>>>>>'
    results = aa.findall('bbbb')
    Data = []
    i = 0
    for result in results:
        print result
        iid = result.get('_id')
        # print type(result.get('_id'))
        QQ = result.get('QQ')
        updateTime = result.get('updateTime')
        dumpdata = {}
        dumpdata['QQ'] = QQ
        dumpdata['updateTime'] = updateTime
        Data.append(dumpdata)
        i += 1
        if result==None:
            print 'xxxxxxxxxxxxx'
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>next'
    output = open('bbbbbbbbbbbbbb.dat', 'w')
    pickle.dump(Data, output)
    pprint.pprint(Data)
    print "Data len:", len(Data)
    print "sum collection:", i

    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>test end!'

def test2():
    print "pickle load start>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    output = open('bbbbbbbbbbbbbb.dat', 'r')
    Data = pickle.load(output)
    for r in Data:
        # print r['QQ']
        pass
    pprint.pprint(Data)
    print "Data len:", len(Data)
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>test end!'


if __name__=='__main__':
    '''
    info = {'QQ':'123456789','updateTime':'987654321','flag':'1'}
    info1 = {'QQ':1092354}
    info2 ={'$set':{'QQ':789645321,'updateTime':444444444}}
    result = {}
    aa = MongoConnector()
    startTime = int(time.time())
    for i in range(1000000,2000000):
        info = {'QQ':i,'updateTime':int(time.time())}
        aa.insert(info,'bbbb')
    #result = aa.find(info1,'bbbb')
    endTime = int(time.time())
    print endTime-startTime

    #print result
    #print result.get('_id')
    #print type(result.get('_id'))
    #if result==None:
        #print 'xxxxxxxxxxxxx'
    #print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    #info1 = {'_id':result.get('_id')}
    #startTime = time.time()
    #aa.update(info1,info2,'bbbb')
    #endTime = time.time()
    #print endTime-startTime
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    '''
    # test()
    test2()

