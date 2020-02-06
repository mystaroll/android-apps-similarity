#!/usr/bin/env python
# encoding=utf8

# File to be run in IPython to inspect and testout androguard API (docs not updated)


import androguard.misc

a1, d1, dx1 = androguard.misc.AnalyzeAPK(
    "./data/apks/0E11713DB82EF4A9340CF9202D02D0620A370A5302CCA4DF9147EFF4C939F80E.apk")