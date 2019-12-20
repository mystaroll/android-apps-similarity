#!/usr/bin/env python
# coding=utf-8
# author   :  Chicho
# running  :  python calculateNodeL12.py
# function :  1. find the apk's nodes number less than 2


import os 

path = "/home/chicho/workspace/repackaged/ViewDroid/experiment/calculateNodes/all_actCnt.csv"

f = open(path)

lines = f.readlines()

i = 0
j = 0
m = 0
for line in lines:
    line = line.replace("\n","")
    segs = line.split(",")
    actCnt = int(segs[1])

#    i = 0 # record node=1
 #   j = 0 # record node=2 


    if actCnt == 1:
        i += 1
    elif actCnt == 2:
        j += 1
    elif actCnt == 3:
        m +=1 

print i 
print j
print m



f.close()

print "all work is done!"
