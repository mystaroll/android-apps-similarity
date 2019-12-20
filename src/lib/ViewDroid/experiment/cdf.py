#!/usr/bin/env python
# coding=utf-8
import os
import numpy as np
import sys
import statsmodels as sm
from numpy import array 
import matplotlib.pyplot as plt 
from scipy.stats import cumfreq



path = "/home/chicho/workspace/repackaged/ViewDroid/experiment/calculateNodes/all_actCnt.csv"

f = open(path)

def get_data(lines):

    sizeArray = []
    for line in lines:
        line = line.replace("\n","")
        segs = line.split(",")

        try:
            actCnt = int(segs[1])
        except:
            print segs[0]

        sizeArray.append(actCnt)


    return array(sizeArray)

lenths = get_data(f.readlines())




def cdf_plot(lenths):
    data =lenths 
    
    counts,bin_edges = np.histogram(data, 300, normed=True)
    cdf = np.cumsum(counts)
    

    plt.plot(bin_edges[1:],cdf,lw=2)
    # if we want to set the color 
    # plt.plot(bin_edges[1:],cdf,lw=2,color='y')

    plt.xlabel('Number of Activity')
    plt.ylabel('CDF')

    plt.grid(True)

    plt.show()


cdf_plot(lenths)



