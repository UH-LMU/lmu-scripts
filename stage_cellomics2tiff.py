#!/usr/bin/python
import datetime
import math, sys, time
import string
import subprocess
import glob
from optparse import OptionParser
import os
import traceback

from mp_cellomics2tiff import CellomicsConverter
from utils import CellomicsUtils

DRY_RUN = False
creator = "creator"

# input directory
INPUT_ROOT = None

# staging directory on compute server
STAGING_ROOT = None

# output root directory on lmu-active
OUTPUT_ROOT = None

cutils = CellomicsUtils()

def stageAndConvert(dir_in):
    dir_in = os.path.join(INPUT_ROOT,dir_in)

    # input image files
    c01s = glob.glob(dir_in + "/*.C01")

    # skip items that are not directories
    if not os.path.isdir(dir_in):
        return

    # skip of not a Cellomics dataset
    if not cutils.isCellomicsDataset(dir_in):
        print "stage_cellomics2tiff: not a C01 dataset:",dir_in
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
    if not os.path.isdir(os.path.join(OUTPUT_ROOT,'log')):
        os.makedirs(os.path.join(OUTPUT_ROOT,'log'))
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
    if not DRY_RUN:
        os.system("rsync -r " + staging_out + " " + dir_out)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time_copy) + "s"

    print >> logfile, "Total time elapsed: " + str(time.time() - start_time) + "s"
    logfile.close()
    print


##
## Main part
##
if __name__=='__main__':

    usage = """%prog [options] input_dir staging_dir output_dir

                Stage and convert CellInsight data to TIF.
                RUN '%prog -h for options.'"""

    parser = OptionParser(usage=usage)
    parser.add_option('-n', '--dryrun', action="store_true", \
                      default=False, help="Print actions but do not execute.")
    parser.add_option('-i', '--input', default='/input', help="Input directory [default: %default].")
    parser.add_option('-s', '--staging', default='/staging', help="Staging directory [default: %default].")
    parser.add_option('-o', '--output', default='/output', help="Output directory [default: %default].")
    
    opts,args = parser.parse_args()
    if opts.dryrun:
        print "DRY RUN"
        DRY_RUN = True

    INPUT_ROOT = opts.input
    STAGING_ROOT = opts.staging
    OUTPUT_ROOT = opts.output

    # lock file
    pidfile_name = os.path.join(STAGING_ROOT, "stage_cellomics2tiff.pid")

    # check if conversion is already running
    if os.path.isfile(pidfile_name):
        print "Conversion is already running, exiting..."
        sys.exit(0)

    # write process id to lock file
    pidfile = open(pidfile_name,'w')
    pid = os.getpid()
    print >> pidfile, str(pid)
    pidfile.close()


    # process all CellInsight datasets in the input directory
    datasets = []
    try:
        datasets = os.listdir(INPUT_ROOT)
    except Exception as e:
        print "Failed to read input directory."
        print e.strerror
        
    for dir_in in datasets:
        try:
            stageAndConvert(dir_in)
        except Exception as e:
            print "Failed to convert " + dir_in
            #print e.strerror
            traceback.print_exc()
            
    # remove lock file
    os.remove(pidfile_name)

    print "stage_cellomics2tiff:","Done."

