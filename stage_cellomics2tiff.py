#!/usr/bin/python
import datetime
import math, sys, time
import string
import subprocess
import glob
import os

from mp_cellomics2tiff import CellomicsConverter
from utils import CellomicsUtils

DRY_RUN = False
creator = "creator"

# input directory on lmu-active
INPUT_ROOT = "/mnt/lmu-active/LMU-active2/users/FROM_CELLINSIGHT"

# staging directory on compute server
STAGING_ROOT = os.path.expanduser("~") + "/staging/"

# lock file
PIDFILE = os.path.join(STAGING_ROOT, "stage_cellomics2tiff.pid")

# output root directory on lmu-active
OUTPUT_ROOT = "/mnt/FROM_CSC_LMU/CellInsight"
#OUTPUT_ROOT = "/home/hajaalin/tmp"
#OUTPUT_ROOT = "/mnt/lmu-active-rw/LMU-active2/users/FROM_CSC_LMU/CellInsight"

cutils = CellomicsUtils()

def stageAndConvert(dir_in):
    dir_in = os.path.join(INPUT_ROOT,dir_in)

    # input image files
    c01s = glob.glob(dir_in + "/*.C01")

    # skip items that are not directories
    if not os.path.isdir(dir_in):
        return

    print "stage_cellomics2tiff INPUT:",dir_in

    # input and output directories on csc-lmu-ubuntu
    head,tail = os.path.split(dir_in)
    staging_in = STAGING_ROOT + tail
    staging_out = staging_in + "_converted"

    # list of converted datasets, in subfolders by user
    converted = glob.glob(OUTPUT_ROOT + "/*/*")
    for c in converted:
        # check if the folder name matches
        if string.find(c,tail + "_converted") != -1 and os.path.isdir(c):
            print "stage_cellomics2tiff: found existing conversion:",c 
            # skip the folder if it has been converted already
            if cutils.isDatasetConverted(dir_in,c):
                #print "stage_cellomics2tiff:","CURRENT", tail + "_converted"
                #print "stage_cellomics2tiff:","CONVERTED",c
                print "stage_cellomics2tiff: existing conversion is up to date, skipping..."
                print
                return
            else:
                print "stage_cellomics2tiff: existing conversion is not complete or up to date."
    
    # Create staging directories
    if not os.path.isdir(staging_in):
        os.makedirs(staging_in)
    if not os.path.isdir(staging_out):
        os.makedirs(staging_out)

    # Create log file
    t = time.time()
    ft = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')
    logfile = open(OUTPUT_ROOT+'/log/%s_stage_cellomics2tiff_%s.log'%(tail,ft),'w')
    start_time = time.time()

    # Copy data to the cluster
    msg ="Copying (rsync) data to " + staging_in + "..."
    print "stage_cellomics2tiff:",msg
    print >> logfile, msg
    if not DRY_RUN:
        os.system("rsync -rt " + dir_in + "/ " + staging_in)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time) + "s"

    # Convert the data
    start_time_convert = time.time()
    msg = "Converting..."
    print "stage_cellomics2tiff:",msg 
    print >> logfile, msg
    if not DRY_RUN:
        converter = CellomicsConverter()
        converter.convert(staging_in,staging_out)
        print >> logfile, "Time elapsed: " + str(time.time() - start_time_convert) + "s"

        # find the creator of the data from metadata
        csv = os.path.join(staging_out,"metadata","asnPlate.csv")
        creator = cutils.findCreator(csv)
        
        # Copy results outside the cluster
        dir_out = os.path.join(OUTPUT_ROOT,creator)
        if not os.path.isdir(dir_out):
            os.makedirs(dir_out)
            
        start_time_copy = time.time()
        msg = "Copying " + staging_out + " to " + dir_out
        print "stage_cellomics2tiff:",msg
        print >> logfile, msg
        os.system("rsync -r " + staging_out + " " + dir_out)
        print >> logfile, "Time elapsed: " + str(time.time() - start_time_copy) + "s"

    print >> logfile, "Total time elapsed: " + str(time.time() - start_time) + "s"
    logfile.close()
    print


if len(sys.argv) > 1:
    print "DRY RUN"
    DRY_RUN = True
    
# check if conversion is already running
if os.path.isfile(PIDFILE):
    print "Conversion is already running, exiting..."
    sys.exit(0)

# write process id to lock file
pidfile = open(PIDFILE,'w')
pid = os.getpid()
print >> pidfile, str(pid)
pidfile.close()

# process all CellInsight datasets in the input directory
datasets = os.listdir(INPUT_ROOT)
for dir_in in datasets:
    stageAndConvert(dir_in)

# remove lock file
os.remove(PIDFILE)

print "stage_cellomics2tiff:","Done."

