#!/usr/bin/env python
import datetime
import os
import sys
import time
import xml.etree.ElementTree as ET

config = sys.argv[1]
tree = ET.parse(config)
root = tree.getroot()

for sync in root:
    user = sync.get("user")
    src = sync.get("src")
    dst = sync.get("dst")
    email = sync.get("email")

    t = time.time()
    ft = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')

    log = "irsync_" + user + "_" + ft + ".log"

    cmd = "irsync -VKr %s %s >& %s" % (src,dst,log)
    print cmd

    os.system(cmd)
