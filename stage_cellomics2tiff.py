#!/usr/bin/python
import datetime
import math, sys, time
import string
import subprocess
import glob
import os

from mp_cellomics2tiff import CellomicsConverter
from utils import CellomicsUtils
    
# input directory on lmu-active
INPUT_ROOT = "/mnt/lmu-active/LMU-active2/users/FROM_CELLINSIGHT"

# staging directory on compute server
STAGING_ROOT = os.path.expanduser("~") + "/staging/"

# output root directory on lmu-active
OUTPUT_ROOT = "/mnt/FROM_CSC_LMU/CellInsight"
OUTPUT_ROOT = "/home/hajaalin/tmp"
#OUTPUT_ROOT = "/mnt/lmu-active-rw/LMU-active2/users/FROM_CSC_LMU/CellInsight"


def stageAndConvert(dir_in):
    dir_in = os.path.join(INPUT_ROOT,dir_in)

    # skip items that are not directories
    if not os.path.isdir(dir_in):
        return

    print "stage_cellomics2tiff:",dir_in

    # input and output directories on csc-lmu-ubuntu
    head,tail = os.path.split(dir_in)
    staging_in = STAGING_ROOT + tail
    staging_out = staging_in + "_converted"

    # skip if results directory exists
    converted = glob.glob(OUTPUT_ROOT + "/*/*")
    #print converted
    for dataset in converted:
        if string.find(dataset,tail + "_converted") != -1:
            print "stage_cellomics2tiff:","CONVERTED",dataset
            print "stage_cellomics2tiff:","CURRENT", tail + "_converted"
            print "stage_cellomics2tiff:",dir_in,"seems to be converted, skipping..."
            print
            return
    
    # Create staging directories
    if not os.path.isdir(staging_in):
        os.makedirs(staging_in)
    if not os.path.isdir(staging_out):
        os.makedirs(staging_out)

    # Create log file
    t = time.time()
    ft = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')
    logfile = open(OUTPUT_ROOT+'/%s_stage_cellomics2tiff_%s.log'%(tail,ft),'w')
    start_time = time.time()

    # Copy data to the cluster
    msg ="Copying (rsync) data to " + staging_in + "..."
    print "stage_cellomics2tiff:",msg
    print >> logfile, msg
    os.system("rsync -r " + dir_in + "/ " + staging_in)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time) + "s"

    # Convert the data
    start_time_convert = time.time()
    msg = "Converting..."
    print "stage_cellomics2tiff:",msg 
    print >> logfile, msg
    converter = CellomicsConverter()
    converter.convert(staging_in,staging_out)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time_convert) + "s"

    # find the creator of the data from metadata
    csv = os.path.join(staging_out,"metadata","asnPlate.csv")
    utils = CellomicsUtils()
    creator = utils.findCreator(csv)
    
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


# process all CellInsight datasets in the input directory
datasets = os.listdir(INPUT_ROOT)
for dir_in in datasets:
    stageAndConvert(dir_in)

##    # Flag the input directory as converted
##    flag = open(flag_converted, 'w')
##    print >> flag,"CONVERTED"
##    flag.close()
    
print "stage_cellomics2tiff:","Done."

