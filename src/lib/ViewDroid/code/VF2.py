#!/usr/bin/env python
# coding=utf-8
# Author    : Chicho
# filename  : VF2.py
# Date      : 2017-06-14
# Function  : compare the original ATG activity transit graph
#             between the original one and the repackaged one
#             if the are the isomorphism 
#             we deem the are similar app pairs

import os
import networkx as nx 
from networkx.algorithms import isomorphism 
import time 


oriGPath = "/home/chicho/workspace/repackaged/ViewDroid/graph/original/"

repGPath = "/home/chicho/workspace/repackaged/ViewDroid/graph/repackaged/"

pairPath = "/home/chicho/workspace/repackaged/repackaging_pairs2.txt"

# create the file 

def createGraph(lines):
    
    # creat a graph

    G = nx.Graph()

    for line in lines:
        line = line.replace("\n","")
        edge = line.split(" ")
        G.add_edge(int(edge[0]),int(edge[1]))


    return G 



def VF2(oriGPath,repGPath):

    f = open(pairPath)

    for line in f.readlines():
        line = line.replace("\n","")
        apks = line.split(",")

        oriapk = apks[0] + ".txt"
        repapk = apks[1] + ".txt"

        tips = "compare the apk pairs {0},{1}".format(apks[0],apks[1])
        print tips 

        oriAPKPath = os.path.join(oriGPath,oriapk)
        repAPKPath = os.path.join(repGPath,repapk)

        if os.path.exists(oriAPKPath) and os.path.exists(repAPKPath):
            orif = open(oriAPKPath)
            tarf = open(repAPKPath)

            G = createGraph(orif.readlines())
            T = createGraph(tarf.readlines())

            start = time.time()

            GM = isomorphism.GraphMatcher(G,T)
            GM1 = isomorphism.GraphMatcher(T,G)


            if GM.subgraph_is_isomorphic():

                print "Graph G and Graph T are isomorphic!"
                print GM.mapping 
                
                end = time.time()
                elapse = end - start 
                
                cmd = "echo {0} >> {1}".format(elapse,"runningtime.txt")
                os.system(cmd)

                cmd = "echo {0},{1} >> {2}".format(apks[0],apks[1],"similarityResult.txt")
                os.system(cmd)

                orif.close()
                tarf.close()

                continue  

            if GM1.subgraph_is_isomorphic():

                print "Graph T and Graph G are isomorphic!"
                print GM1.mapping

                end = time.time()

                elapse = end - start

                cmd = "echo {0} >>{1}".format(elapse,"runningtime.txt")
                os.system(cmd)

                cmd = "echo {0},{1} >>{2}".format(apks[0],apks[1],"similarityResult.txt")

                orif.close()
                tarf.close()


VF2(oriGPath,repGPath)

print VF2
