#!/usr/bin/env python
# coding=utf-8
# author    :   Chicho
# running   :   python calculateAct.py 
# function  :   1. calculate the number of Activity of GT 
#               2. parse the Log file 
#               3. we parse the LOG file original_APKACTLOG to use the larger number the AndroidManifset.xml 
#                  or the a3e result 
#                  choose the larger one Act 

import os 

oriPath = "/home/chicho/workspace/repackaged/ViewDroid/experiment/calculateNodes/LOG/original_APKACTLOG"

repPath = "/home/chicho/workspace/repackaged/ViewDroid/experiment/calculateNodes/LOG/repackaged_APKACTLOG"


def calculateNodes(path):

    f = open(path)
    lines = f.readlines()
    
    fileName = path.split("/")[-1].split("_")[0] + "_actCnt"
    print fileName

    

    for line in lines:
        line = line.replace("\n","")
        segs = line.split(",")

        actCnt1 = int(segs[1])
        actCnt2 = int(segs[2])

        actCnt = max(actCnt1,actCnt2)

        cmd = "echo {0},{1} >> {2}".format(segs[0],actCnt,fileName)
        os.system(cmd)

        print segs[0]


    f.close()



calculateNodes(oriPath)
calculateNodes(repPath)
