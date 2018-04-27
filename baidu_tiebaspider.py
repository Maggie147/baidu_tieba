# -*- coding: utf-8 -*-
'''
    @File    baidut tieba
    @Author  tx
    @Created On 2018-04-26
    @Updated On 2018-04-27
'''
import os
import re
import sys
import time
import json
# import chardet
import pprint
import requests
from lxml import etree
from bs4 import BeautifulSoup as bs
from multiprocessing.dummy import Pool
pwd = os.path.dirname(os.path.realpath(__file__))           #pwd2 = sys.path[0]
# pardir = os.path.abspath(os.path.join(pwd, os.pardir))


def get_file_data(fpath, ftype=None):
    try:
        if ftype == 'json':
            with open(fpath, 'r') as fjp:
                buf = json.load(fjp)
        else:
            with open(fpath, 'r') as fp:
                buf = fp.read()
        return buf
    except Exception as e:
        print(e)
        return None


def format_date(buf):
    if not buf:
        return None
    cldate = buf.strip().split(' ')
    cldlen = len(cldate[0])
    # print("cldate0: ", cldate[0])
    # print("cldate1: ", cldate[1])
    print("cld_len: ", cldlen)

    if cldlen > 6:
        print("normal date: ", cldate)
        restr = r'(\d{4}).*?(\d{1,2}).*?(\d{1,2})'
        value = re.findall(restr, cldate[0], re.S | re.M)
        realdate = '-'.join(value[0]) + ' ' + cldate[1]
    else:
        print("not normal date: ", cldate)
        tstrp_today = time.localtime(time.time())
        ymd = time.strftime('%Y-%m-%d', tstrp_today).split('-')
        if '昨' in cldate[0]:
            day = int(ymd[-1]) -1
            realdate = str(ymd[0]) + '-' + str(ymd[1]) + '-' + str(day) + ' '+ cldate[1]
        elif '前' in cldate[0]:
            day = int(ymd[-1]) -2
            realdate = str(ymd[0]) + '-' + str(ymd[1]) + '-' + str(day) + ' '+ cldate[1]
    print("realdate: ", realdate)
    try: 
        # 2018-04-26 10:01
        timestrp = time.strptime(realdate, "%Y-%m-%d %H:%M")
        time_stamp = int(time.mktime(timestrp))
    except Exception as e:
        print(e)
        time_stamp = int(time.time())
    print(time_stamp)

def test_format_date():
    buf = '  2018年04月26日 10:01'
    # buf = '  2018年4月26日 10:01 '
    # buf = '  昨天 10:01 '
    ftime =  format_date(buf)


class BaiduTieba(object):
    def __init__(self, username, dpath):
        self.user   =  username
        self.fpath  = self._get_path(dpath)
        self.header = self._get_header()
        self.mySession = requests.session()
        self.portrait  = self._get_portrait()
        self._check_portrait()


    def _get_header(self, cookie=None, para=None):
        header  = {}
        header['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        try:
            header.update(self.header)
        except Exception as e:
            pass
        if cookie:
            header['Cookie']  = cookie
        if para:
            header.update(para)
        return header

    def _get_path(self, dpath):
        path = os.path.realpath(dpath)
        mypath = os.path.join(path, self.user)
        if not os.path.exists(mypath):
            os.makedirs(mypath)
        return mypath

    def _save_data(self, buf, fname, ftype=None):
        try:
            fullpath = os.path.join(self.fpath, fname)
            path = os.path.split(fullpath)[0]
            if not os.path.exists(path):
                os.makedirs(path)
            if ftype == 'json':
                with open(fullpath, 'w') as fjp:
                    json.dump(buf, fjp)
            else:
                with open(fullpath, 'w') as fp:
                    fp.write(buf.encode('gbk', 'ignore'))
            return True
        except Exception as e:
            print(e)
            return False

    def _my_request(self, url):
        try:
            res = self.mySession.get(url, headers=self.header)
            if str(res.status_code)[0] != '2':
                print("request failed, URL: "+url)
                return None
            # res.encoding = 'utf-8'
            return res.text
        except Exception as e:
            print(e)
            return None

    def _check_portrait(self):
        if not self.portrait:
            print('get portrait failed.')
            sys.exit(1)
        else:
            lens = len(self.portrait)
            if lens < 30 or lens> 32:
                print('invalid portrait.')
                sys.exit(1)
        print('get portrait: '+self.portrait)
        print('portrait len: '+str(len(self.portrait)))

    def _match_portrait(self, buf):
        try:
            result = ''
            restr = r'<script>.*?App\.onPageletArrive\({.*?"options".*?page_userInfo(.*?)};'
            ret = re.findall(restr, buf, re.S | re.M)
            if not ret:
                print("Step1: _match_portrait failed!!")
                return None
            restr = r"'portrait'.*?:(.*?)',"
            userInfo = re.findall(restr, str(ret), re.S | re.M)
            if not userInfo:
                print("Step2: _match_portrait failed!!")
                return None
            result = str(userInfo[0]).replace("'", '').strip()
            return result
        except Exception as e:
            print(e)
            return None

    def _get_portrait(self):
        url  = 'https://www.baidu.com/p/{}?from=tieba'.format(self.user)
        try:
            resp = self._my_request(url)
            if  not resp:
                print("request baidu tieba main_page failed!!")
                return None
            self._save_data(resp, 'main_page_{}.html'.format(self.user))
            if not resp or resp.find('portrait') == -1:
                return None
            portrait = self._match_portrait(resp)
            return portrait if portrait else None
        except Exception as e:
            print(e)
            return None


    def _match_dicdata(self, buf):
        try:
            if not buf or buf.find('tplContent') ==-1:
                print("invalid topicTie. (not found 'tplContent') ")
                return None

            begin = buf.find('(')
            end = buf.rfind(')')
            tmp = buf[begin+1:end]

            if tmp.find('"options') != -1:
                rm_begin = tmp.find('"options')
                rm_len = tmp[rm_begin:].rfind('},')
                data = tmp[:rm_begin] + tmp[rm_begin+rm_len+len('},'):]
            else:
                print("no option")
                data = tmp
            try:
                result = eval(data)                 # if isinstance(result, dict):
                return result
            except Exception as e:
                print('eval failed')
                print(data)
                return None
        except Exception as e:
            print(e)
            print("where!!!!")
            return None

    def get_topcontent(self, buf):
        print('get_topcontent')
        root = etree.HTML(buf)
        data = root.xpath('//cc/div[@id]/text()')
        if not data:
            print("not get topic content")
        try:
            results = ''.join(data)
            results = results.strip().replace('\/', '/')
            results = results.replace('\\\\', '/')
            return results if results else None
        except Exception as e:
            print(e)
            return None

    def analyse_topic(self, buf):
        root = etree.HTML(buf)
        feed_list   = root.xpath('//li[@class="feed-item clearfix item-zhuti"]')
        feeds = []
        for feed_item in feed_list:
            feed = {}
            feed['feed_user']  = self.user
            feed['feed_type']  = feed_item.xpath('.//div[@class="feed-title"]/text()')[0].encode('raw_unicode_escape')
            feed['feed_title'] = feed_item.xpath('.//div/a[@class="feed-content"]/text()')[0].encode('raw_unicode_escape')
            feed_href          = feed_item.xpath('.//div/a[@class="feed-content"]/@href')[0]
            feed['feed_href']  = feed_href.replace('\/', '/') if feed_href else None
            feed['feed_from']  = feed_item.xpath('.//div/a[@class="feed-from"]/text()')[0].encode('raw_unicode_escape')
            feed_time          = feed_item.xpath('.//span[@class="datetime"]/text()')[0].encode('raw_unicode_escape')
            feed['feed_time']  = format_date(feed_time)
            feed['spid_time']  = time.time()
            if feed['feed_href']:
                print(feed['feed_href'])
                resp = self._my_request(feed['feed_href'])
                if  not resp:
                    print("request tie_href failed!!")
                    feed['feed_conte'] =None
                else:
                    feed['feed_conte'] = self.get_topcontent(resp)
            feeds.append(feed)
        return feeds

    def analyse_reply(self, buf):
        root = etree.HTML(buf)
        feed_list   = root.xpath('//li[@class="feed-item clearfix item-reply"]')
        feeds = []
        for feed_item in feed_list:
            feed = {}
            feed['feed_user']  = self.user
            feed['feed_type']  = feed_item.xpath('.//div[@class="feed-title"]/text()')[0].encode('raw_unicode_escape')
            body = feed_item.xpath('.//div[@class="feed-body clearfix"]/div[@class="wordwrap"]')[0]
            href  = body.xpath('./a[@href]/@href')[0]
            feed['feed_href'] = href.replace('\/', '/') if href else None
            feed['feed_conte'] = body.xpath('./a[@href]/text()')[0].encode('raw_unicode_escape')
            feed['feed_title'] = body.xpath('.//div[@class="quoted clearfix"]//a[@class="feed-content"]/text()')[0].encode('raw_unicode_escape')
            feed['feed_from']  = body.xpath('.//div[@class="quoted clearfix"]//a[@class="feed-from"]/text()')[0].encode('raw_unicode_escape')
            feed_time          = feed_item.xpath('.//span[@class="datetime"]/text()')[0].encode('raw_unicode_escape')
            feed['feed_time']  = format_date(feed_time)
            feed['spid_time']  = time.time()
            feeds.append(feed)
        return feeds


    def _get_comments(self, ttype):                      #ttype: zhuti, reply
        contents = []
        pg = 0
        while True:
            pg  += 1
            url = 'https://www.baidu.com/p/sys/data/tieba/feed?rec=1000008&portrait={}&pn={}&type={}&t=1524715347871'.format(self.portrait, pg, ttype)
            print(url)
            print("pg: "+ str(pg))

            resp = self._my_request(url)
            if resp:
                values = self._match_dicdata(resp)
                if values:
                    try:
                        self._save_data(values.get('tplContent'), '{}Tie_{}_{}.html'.format(ttype, self.user, pg))
                    except Exception as e:
                        print("save failed!!")

                    if ttype == 'zhuti':
                        one_cont = self.analyse_topic(values.get('tplContent'))
                        contents.extend(one_cont)
                    elif ttype == 'reply':
                        one_cont = self.analyse_reply(values.get('tplContent'))
                        contents.extend(one_cont)

                    hasMore = values.get('modelValue').get('hasMore')
                    if not hasMore or hasMore.find('no') != -1:                 # hasMore, None: 可能是首页没有该字段;  hasMore, noMoreFeed:表没有更多内容了
                        print(hasMore)
                        break
            else:
                break
        self._save_data(contents, '{ttype}_{user}.json'.format(ttype=ttype, user=self.user), ftype='json')


    def get_topicTie(self):
        topic_type = 'zhuti'
        self._get_comments(ttype=topic_type)


    def get_replyTie(self):
        topic_type = 'reply'
        self._get_comments(ttype=topic_type)



def main():
    username = "muliqun7316"
    fpath    = './output'
    baidu = BaiduTieba(username, fpath)
    baidu.get_topicTie()
    # baidu.get_replyTie()



if __name__ == '__main__':
    main()
    # test_format_date()