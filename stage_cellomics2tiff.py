#!/usr/bin/python
import datetime
import math, sys, time
import subprocess
import glob
import os

from mp_cellomics2tiff import CellomicsConverter
    
# input directory on lmu-active
dir_in_root = "/mnt/lmu-active/LMU-active2/users/FROM_CELLINSIGHT"

# staging directory on compute server
staging_root = os.path.expanduser("~") + "/staging/"

# output root directory on lmu-active
dir_out_root = "/mnt/FROM_CSC_LMU/CellInsight"
dir_out_root = "/home/hajaalin/tmp"
#dir_out_root = "/mnt/lmu-active-rw/LMU-active2/users/FROM_CSC_LMU/CellInsight"


# process all CellInsight datasets in the input directory
datasets = os.listdir(dir_in_root)
for dir_in in datasets:
    dir_in = os.path.join(dir_in_root,dir_in)
    print dir_in
    
    if not os.path.isdir(dir_in):
        continue

    # input and output directories on csc-lmu-ubuntu
    head,tail = os.path.split(dir_in)
    staging_in = staging_root + tail
    staging_out = staging_in + "_converted"

##    # skip if directory is marked as converted
##    flag_converted = os.path.join(dir_in_root, dir_in, "CONVERTED")
##    if os.path.isfile(flag_converted):

    # skip if results directory exists
    if os.path.isdir(os.path.join(dir_out_root,tail + "_converted")):
        print dir_in, "seems to be converted, skipping..."
        continue
    
    # Create staging directories
    if not os.path.isdir(staging_in):
        os.makedirs(staging_in)
    if not os.path.isdir(staging_out):
        os.makedirs(staging_out)

    # Create log file
    t = time.time()
    ft = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')
    logfile = open(dir_out_root+'/%s_stage_cellomics2tiff_%s.log'%(tail,ft),'w')
    start_time = time.time()

    # Copy data to the cluster
    msg ="Copying (rsync) data to " + staging_in + "..."
    print msg
    print >> logfile, msg
    os.system("rsync -r " + dir_in + "/ " + staging_in)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time) + "s"

    # Convert the data
    start_time_convert = time.time()
    msg = "Converting..."
    print msg 
    print >> logfile, msg
    converter = CellomicsConverter()
    converter.convert(staging_in,staging_out)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time_convert) + "s"

    # Copy results outside the cluster
    start_time_copy = time.time()
    msg = "Copying results to " + dir_out_root
    print msg
    print >> logfile, msg
    os.system("rsync -r " + staging_out + " " + dir_out_root)
    print >> logfile, "Time elapsed: " + str(time.time() - start_time_copy) + "s"

    print >> logfile, "Total time elapsed: " + str(time.time() - start_time) + "s"
    logfile.close()

##    # Flag the input directory as converted
##    flag = open(flag_converted, 'w')
##    print >> flag,"CONVERTED"
##    flag.close()
    
print "Done."

