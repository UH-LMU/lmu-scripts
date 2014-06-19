#!/usr/bin/python
import math, sys, time
import subprocess
import glob
import os
import logging

from mp_cellomics2tiff import CellomicsConverter

def cellomics2tiff((file_in,dir_out)):
    print "joo"
    
# input directory on lmu-active
dir_in = sys.argv[1]
# output root directory on lmu-active
dir_out_root = sys.argv[2]

# input and output directories on csc-lmu-ubuntu
head,tail = os.path.split(dir_in)
staging_root = os.path.expanduser("~") + "/staging/"
staging_in = staging_root + tail
staging_out = staging_in + "_converted"

# Create staging directories
if not os.path.isdir(staging_in):
    os.makedirs(staging_in)
if not os.path.isdir(staging_out):
    os.makedirs(staging_out)

# Create log file
logging.basicConfig(filename=staging_out+'/stage_cellomics2tiff.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

start_time = time.time()

# Copy data to the cluster
msg ="Copying (rsync) data to " + staging_in + "..."
print msg
logging.info(msg)
os.system("rsync -r " + dir_in + "/ " + staging_in)
logging.info("Time elapsed: " + str(time.time() - start_time) + "s")

# Convert the data
start_time_convert = time.time()
msg = "Converting..."
print msg 
logging.info(msg)
converter = CellomicsConverter()
converter.convert(staging_in,staging_out)
logging.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")

# Copy results outside the cluster
start_time_copy = time.time()
msg = "Copying results to " + dir_out_root
print msg
logging.info(msg)
os.system("rsync -r " + staging_out + " " + dir_out_root)
logging.info("Time elapsed: " + str(time.time() - start_time_copy) + "s")

logging.info("Total time elapsed: " + str(time.time() - start_time) + "s")
print "Done."

