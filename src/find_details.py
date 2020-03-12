#!/usr/bin/env python
# encoding=utf8

#
#echo "Report: $1, pair searched: $2"
#
#if [ -z "$3" ]
#then
#  LINES=100
#else
#  LINES="$3"
#fi
#
#LINES=$(cat $1 | grep  "###($2)###" | cut -f1 -d:)
#
#if [ -z "$DETAILS" ]
#then
#  echo "Searched Pair Not Found In The Log."
#else
#  echo "$DETAILS"
#fi

import re
import sys

if len(sys.argv) > 2 :
    print "Reading details from file"

    report_path = sys.argv[1]

    pair_id = sys.argv[2]

    with open(report_path) as f:
        full_log = f.read()
        start=full_log.find("###(%s)###" % pair_id)
        end=full_log.find("CURRENT ANALYSIS",start )
        print full_log[start:end]
else:
    print "Reading details from stdin"
    pair_id = sys.argv[1]
    with sys.stdin as f:
        full_log = f.read()
        start=full_log.find("###(%s)###" % pair_id)
        end=full_log.find("CURRENT ANALYSIS",start )
        print full_log[start:end]

# To get smaller details
#grep -E -v "DELETED|ADDED|---|^[ ]*\$"