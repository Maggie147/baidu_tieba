# -*- coding: utf-8 -*-
'''
    @File    baidut tieba
    @Author  tx
    @Created On 2018-05-01
    @Updated On 2018-05-07
'''
import os
import sys
import time
import pprint
from collections import OrderedDict
from spylib import mongo_operate
from spylib.common import DEBUG, save_data
from spiders.baidu_tieba_spider import BaiduTieba
from multiprocessing.dummy import Pool
reload(sys)
sys.setdefaultencoding('utf8')
pwd = os.path.dirname(os.path.realpath(__file__))


class BaiduTiebaMaster(object):
    def __init__(self, output, conn):
        self.output = output
        self.db = conn
        self.fetchedInfo = {}

    def read_accounts(self, tableName='TLoginInfo'):
        try:
            local_time = int(time.time())
            # query = {'H010001':'1270040', 'B040002':{'$exists': True}}
            query = {"H010014": {"$gt":local_time-7200}, "H010001":"1270040"}
            field = ['B040002']
            values  = self.db.findall(tableName, query, field)
            results = [item.get('B040002') for item in values if item.get('B040002')]
            results = list(set(results))
            return results
        except Exception as e:
            print(e)
            return None


    def get_lsttime(self, tableName='TBbsbaiduLst'):
        try:
            results = {}
            values = self.db.findall(tableName)
            for item in values:
                account = item.get('account')
                lsttime = item.get('lsttime')
                if account and lsttime:
                    results.update({account:lsttime})
            # results = {item.get('account'):item.get('lsttime') for item in values if item.get('account')}
            return results
        except Exception as e:
            print(e)
            return None

    def update_lsttime(self, value, tableName='TBbsbaiduLst'):
        try:
            info = {'account': value['account']}
            value = {'$set': {'lsttime': int(value['lsttime'])}}
            self.db.update(info, value, tableName)
        except Exception as e:
            print(e)
            print('Update lsttime error!!!')



    def init_accounts(self):
        print("get all baidutieba accounts(nickname)")
        accounts = self.read_accounts(tableName='TLoginInfo')
        if not accounts:
            return None

        # get fetched accounts info
        print("get fetched accounts info")
        try:
            fetchedInfo = self.get_lsttime(tableName='TBbsbaiduLst')
            self.fetchedInfo = fetchedInfo if fetchedInfo else {}
        except Exception as e:
            print(e)
        return accounts


    def TryFetchInfo(self, account):
        print("NickName: "+str(account))

        baidu = BaiduTieba(account, self.output)
        tryRet = baidu.check_portrait()
        if not tryRet:
            return False

        lsttime = self.fetchedInfo.get(account)
        print("lsttime:" + str(lsttime))

        try:
            topValues = baidu.get_topicTie(lsttime)
        except Exception as e:
            print(e)
            print("Fetched topicTi {}, failed!!!!!!!".format(account))
            topValues = None

        try:
            repValues = baidu.get_replyTie(lsttime)
        except Exception as e:
            print(e)
            print("Fetched replyTie {}, failed!!!!!!!".format(account))
            repValues = None


        if topValues or repValues:
            lstT = topValues[0].get('feed_time') if topValues else None
            lstR = repValues[0].get('feed_time') if repValues else None
            newtime = lstT if lstT > lstR else lstR
            print("lstT:" + str(lstT))
            print("lstR:" + str(lstR))
            print("newtime:" + str(newtime))

            upInfo  = {'account':account, 'lsttime': newtime}
            self.update_lsttime(upInfo, tableName='TBbsbaiduLst')
        else:
            # print("Fetched  {}, No data!!!".format(account))                  # maybe no data, maybe no new data
            pass

        print("Fetched  {}, End.\n".format(account))
        return True


def main():
    dbConn = mongo_operate.MongoConnector()
    poolSZ = 5
    dirs = pwd.split('/')
    output = os.path.join('/home/', dirs[2], 'bbsInfo')
    master = BaiduTiebaMaster(output, dbConn)

    while True:
        try:
            accounts = master.init_accounts()
            # accounts = [u'fengbaby0']                      # for test account

            if not accounts:
                print("accounts are None")
                print('sleep...')
                time.sleep(60*60)
                continue

            print("accounts len: "+str(len(accounts)))

            pool = Pool(poolSZ)
            results = pool.map(master.TryFetchInfo, accounts)
            pool.close()
            pool.join()

            print('sleep...')
            time.sleep(60*60)
        except Exception as e:
            print(e)
            print('sleep...')
            time.sleep(60*60)
            continue



if __name__ == "__main__":
    main()