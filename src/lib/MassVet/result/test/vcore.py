#!/usr/bin/env python
# coding=utf-8
import networkx as nx 
import numpy as np 
import os


graphPath = "/home/chicho/workspace/repackaged/MassVet/sample/"

def createGraph(lines):

    GL = []

    i = 0

    while(i<len(lines)):
        line = lines[i]

        if " " not in line:
            Gname = line.replace("\n","")

            Gname = nx.MultiDiGraph()

            i = i + 1 

            line = lines[i]

            while ((" " in line) and (i < len(lines))):
                line = line.replace("\n","")
                edge = line.split(" ")
                Gname.add_edge(int(edge[0]),int(edge[1]))
                
                i = i + 1

                if i < len(lines):
                    line = lines[i]


        if Gname not in GL:
            GL.append(Gname)


    return GL 






def readFile(GPath):

    fileList = os.listdir(GPath)

    for file in fileList:
        print file 
        fPath = os.path.join(GPath,file)
        f = open(fPath)

        lines = f.readlines()

        GL = createGraph(lines)

    

        if len(GL)!=0:

            for G in GL:
                print "*************************************" 
                indexNo = GL.index(G)
                cmd = "graph{0}".format(indexNo)
                print cmd 

                print "graph edges"
                print G.edges()
                

                if len(G.edges())<3:
                    continue 

                outDegreeDict = G.out_degree()
                cycleList = list(nx.simple_cycles(G))
                VectorDict = {}
                dfsNodeList = list(nx.dfs_preorder_nodes(G))# 深度遍历节点的先后顺序
                
                print "dfsNodeList"
                print dfsNodeList
                print "cycleList"
                print cycleList
                print "outDegreeDict"
                print outDegreeDict

                eachNode = []

                for i in range(len(dfsNodeList)):
                    eachNode.append(i) 
                    if dfsNodeList[i] not in VectorDict.keys():
                        VectorDict[dfsNodeList[i]]= eachNode
                        eachNode = [] 
                
                print "VectorDict"
                print VectorDict
                

                for key in outDegreeDict.keys():
                    eachNode = VectorDict[key]
                    eachNode.append(outDegreeDict[key])
                    eachNode.append(0)
                    VectorDict[key]=eachNode
                
                print VectorDict


                if len(cycleList)!=0:
                    for cycle in cycleList:
                        for ele in cycle:
                            eachNode = VectorDict[ele]
                            eachNode[2] += 1
                            VectorDict[ele] = eachNode

                print "VectorDict"
                print VectorDict


                # calculate the vcore 
                
                factor = np.zeros(3)

                for edge in G.edges():
                    node1 = edge[0]
                    node2 = edge[1]
                    
                    factor += np.array(VectorDict[node1]) + np.array(VectorDict[node2])

                print factor
                
            

                cmd = "echo {0},{1}>>{2}".format(file,factor,"vcore.csv")
                os.system(cmd)


                cmd = "echo {0},{1},{2},{3}>>{4}".format(file,factor[0],factor[1],factor[2],"vcoreDetail.csv")
                os.system(cmd)
    
    
readFile(graphPath)
