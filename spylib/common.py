# -*- coding: utf-8 -*-
'''
    @File    baidut tieba
    @Author  tx
    @Created On 2018-04-26
    @Updated On 2018-04-28
'''
import os
import sys
import time
import json


g_iDEBUG='1'
def DEBUG(value):
    if g_iDEBUG=="1":
        t=time.strftime("%Y-%m-%d %H:%M:%S")
        filename=sys.argv[0][sys.argv[0].rfind(os.sep)+1:]
        print "[python][%s,%s]:%s"%(filename,t,value)


def get_data(fpath, ftype=None):
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


def save_data(buf, fpath, fname, ftype=None):
    try:
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fullpath = os.path.join(fpath, fname)
        if ftype == 'json':
            with open(fullpath, 'w') as fjp:
                json.dump(buf, fjp)
            print("Save data suceess, dir: {}".format(fullpath))
        else:
            with open(fullpath, 'w') as fp:
                fp.write(buf.encode('utf-8', 'ignore'))
        return True
    except Exception as e:
        # print(e)
        return False


def str_2_dic(src_string):
    try:
        dst_string = ''
        dst_string = eval(src_string)
    except Exception as e:
        try:
            dst_string = repr(src_string)
        except Exception as e:
            print e
    if isinstance(dst_string, str):
        str_2_dic(dst_string)
    if isinstance(dst_string, dict):
        return dst_string

def get_value(buf, begin_str='', head_str='', tail_str=''):
    result_buf = ''
    try:
        if not begin_str:
            buff = buf
        else:
            buff_p = buf.find(begin_str)
            if buff_p != -1:
                buff = buf[buff_p+len(begin_str):]
            else:
                buff = buf

        begin = buff.find(head_str)
        if begin != -1:
            if tail_str  != -1:
                end = buff[begin+len(head_str):].find(tail_str)
                if end:
                    result_buf = buff[begin+len(head_str): begin+len(head_str)+end]
                else:
                    result_buf = buff[begin+len(head_str): ]
            else:
                result_buf = buff[begin+len(head_str):]
        else:
            print "no find head_str"
    except Exception as e:
        print e, " get_value, error!!!"
    return result_buf
