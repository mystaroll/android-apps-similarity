#!/usr/bin/env python
# coding=utf-8
# download repackaging pairs

import os
import argparse


parser = argparse.ArgumentParser(
    description='This script downloads a dataset containing pairs of (original,repackaged) apk\'s')


parser.add_argument("-s", default="groundtruth.txt",
                    help="Source list of pairs")
parser.add_argument("-l",
                    help="Download only first {l} pairs of the source list", type=int)
args = parser.parse_args()
sourceFile = args.s

originalDir = "apks"

if not os.path.exists(sourceFile):
    print "Can't find source list file. %s nor data/%s exist" % sourceFile
    exit(-1)

if not os.path.exists(originalDir):
    os.makedirs(originalDir)

originalList = os.listdir(originalDir)

APIKEY = "a52054307648be3c6b753eb55c093f4c2fa4b03e452f8ed245db653fee146cdd"
# f = open(sourceFile)

# exit(0)

with open(sourceFile) as f:
    fileLines = f.readlines()
    linesToDownload = (len(fileLines) if args.l == None else args.l)
    print "About to download %s pairs" % linesToDownload
    for line in fileLines[:linesToDownload]:

        line = line.replace("\n", "")

        [SHA256_ORIGINAL, SHA256_REPACKAGE, _] = line.split(",")

        curl_command = 'cd {0} && curl -O --remote-header-name -G -d apikey={1} -d sha256={2} https://androzoo.uni.lu/api/download'
        if not (SHA256_ORIGINAL + ".apk") in originalList:
            print "Download apk...."
            cmd = curl_command.format(originalDir,
                                      APIKEY, SHA256_ORIGINAL)
            os.system(cmd)
        if not (SHA256_REPACKAGE + ".apk") in originalList:
            cmd = curl_command.format(originalDir,
                                      APIKEY, SHA256_REPACKAGE)
            os.system(cmd)

print "\nDataset up to date.\n"
