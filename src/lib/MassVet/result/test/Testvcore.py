#!/usr/bin/env python
# coding=utf-8
import networkx as nx 
import os
import matplotlib.pyplot as plt 
import numpy as np


G = nx.MultiDiGraph()

G.add_edges_from([(0,1),(1,2),(1,3),(1,3),(1,3),(1,4),(4,1),(0,5),(5,6),(6,7),(0,8),(0,0),(0,0)])

outDegreeDict=G.out_degree()

cycleList=list(nx.simple_cycles(G))

VectorList = []


for node in G.nodes():

    eachnode = [0]*3

    eachnode[0] = node 

    eachnode[1] = outDegreeDict[node]

    VectorList.append(eachnode)


print VectorList

for cycle in cycleList:
    for ele in cycle:
    
        nodeVec=VectorList[ele]
        nodeVec[2] += 1


print VectorList

print G.edges()
factor = np.zeros(3)
Den=0

for edge in G.edges():
    node1 = edge[0]
    node2 = edge[1]

    factor += np.array(VectorList[node1]) + np.array(VectorList[node2])
    Den += 1 + 1


print factor

for i in range(3):
    factor[i] = factor[i]*1.0/Den 


print factor 


