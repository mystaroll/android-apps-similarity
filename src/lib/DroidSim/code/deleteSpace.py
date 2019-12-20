#!/usr/bin/env python
# coding=utf-8

'''
delete the space line of the file 
'''

import os

oriPath = "/home/chicho/workspace/repackaged/DroidSIM/delete/original/"

repPath = "/home/chicho/workspace/repackaged/DroidSIM/delete/repackaged/"

orioutPath = "/home/chicho/workspace/repackaged/DroidSIM/delete/original1/"

repoutPath = "/home/chicho/workspace/repackaged/DroidSIM/delete/repackaged1/"


def deleteSpace(path,outputPath):

    fileList = os.listdir(path)

    for file in fileList:

        filePath = os.path.join(path,file)

        outfilePath = os.path.join(outputPath,file)
        f = open(filePath)

        for line in f.readlines():

            if line == "\n":
                continue

            line = line.replace("\n","")
            cmd = "echo '{0}' >> {1}".format(line,outfilePath)
            os.system(cmd)


deleteSpace(oriPath,orioutPath)
deleteSpace(repPath,repoutPath)

print "all work is done!"



