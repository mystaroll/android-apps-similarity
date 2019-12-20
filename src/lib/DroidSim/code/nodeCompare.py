#!/usr/bin/env python
# coding=utf-8
# filename   : nodeCompare.py
# author     : Chicho
# date       : 2017-07-04
# version    : V 1.0 
# function   : compare the apk whose node has delete the ads or not 

import os

oriPath = "/home/chicho/workspace/repackaged/DroidSIM/original/"

repPath = "/home/chicho/workspace/repackaged/DroidSIM/repackaged/"

oridelete = "/home/chicho/workspace/repackaged/DroidSIM/delete/original/"

repdelete = "/home/chicho/workspace/repackaged/DroidSIM/delete/repackaged/"

oriCntList =[]
repCntList = []

oridelCntList = []
repdelCntList = []


def calcualteNodes(path):

    apkList = os.listdir(path)
    
    countList = []
    for apk in apkList:
        apkPath = os.path.join(path,apk)

        f = open(apkPath)
        LineList = f.readlines()

        

        count = 0

        for line in LineList:
            if ":" and ";" in line:
                count += 1

        countList.append(count)

    sumCnt = sum(countList) 
    print sumCnt

calcualteNodes(oriPath)
calcualteNodes(repPath)
calcualteNodes(oridelete)
calcualteNodes(repdelete)
