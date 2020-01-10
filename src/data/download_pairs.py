#!/usr/bin/env python
# coding=utf-8
# download repackaging pairs

import os
import argparse


parser = argparse.ArgumentParser(
    description='This script downloads a dataset containing pairs of (original,repackaged) apk\'s')


parser.add_argument("-s", default="common.txt",
                    help="Source list of pairs")
parser.add_argument("-l",
                    help="Download only first {l} pairs of the source list", type=int)
args = parser.parse_args()
print "args.l: " + str(args.l)
sourceFile = args.s

originalDir = "pairs/original"

repackagedDir = "pairs/repackaged"


if not os.path.exists(sourceFile):
    print "Can't find source list file. %s nor data/%s exist" % sourceFile
    exit(-1)

if not os.path.exists(originalDir):
    os.makedirs(originalDir)

if not os.path.exists(repackagedDir):
    os.makedirs(repackagedDir)

originalList = os.listdir(originalDir)

repackagedList = {}

APIKEY = "a52054307648be3c6b753eb55c093f4c2fa4b03e452f8ed245db653fee146cdd"
# f = open(sourceFile)

# exit(0)

with open(sourceFile) as f:
    fileLines = f.readlines()
    linesToDownload = (len(fileLines) if args.l == None else args.l)
    print "About to download %s pairs" % linesToDownload
    for line in fileLines[:linesToDownload]:

        line = line.replace("\n", "")

        [SHA256_ORIGINAL, SHA256_REPACKAGE] = line.split(",")

        apkfile = SHA256_ORIGINAL + ".apk"

        if not apkfile in originalList:
            print "Download apk...."
            curl_command = 'cd {0} && curl -O --remote-header-name -G -d apikey={1} -d sha256={2} https://androzoo.uni.lu/api/download'
            cmd = curl_command.format(originalDir,
                                      APIKEY, SHA256_ORIGINAL)
            os.system(cmd)
            cmd = curl_command.format(repackagedDir,
                                      APIKEY, SHA256_REPACKAGE)
            os.system(cmd)

print "\nDataset up to date.\n"
