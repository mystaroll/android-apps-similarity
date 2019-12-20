#!/usr/bin/env python
# coding=utf-8

import os 
import math
from numpy import array
import numpy as np
import pylab as pl

nodePath = "/home/chicho/workspace/repackaged/ViewDroid/experiment/calculateNodes/all_actCnt"

f = open(nodePath)

def get_data(lines):

    sizeArry= []

    for line in lines:
        line = line.replace("\n","")

        segs = line.split(",")

        try:
            actCnt = int(segs[1])
        except:
            print segs[0]

        sizeArry.append(actCnt)

    return array(sizeArry)

lenths = get_data(f.readlines())


def draw_hist(lenths):
    data = lenths

    bins = np.linspace(min(data),100,20)

    pl.hist(data,bins)

    pl.ylabel('Number of Applications')

    pl.title('Distribution of the activity node number ')

    pl.show()


draw_hist(lenths)

