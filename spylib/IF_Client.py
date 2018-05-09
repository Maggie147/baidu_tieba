'''
Created on 2015-8-2

@author: kk
'''
import bhmIPC
import string
import sys

def main():
    if len(sys.argv)<3:
        print '''Usage:IF_Client.py cmd data
        if data contain multi lines ,they should be included in \"\"'''
        sys.exit()
    ipc=bhmIPC.IPCModule("C","/tmp/IF_IPC")
    data=string.join(sys.argv[1:],'\x06')
    ipc.SendMsg(data)
if __name__ == "__main__":
    main()
