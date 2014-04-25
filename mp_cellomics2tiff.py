#!/usr/bin/python
import math, sys, time
import multiprocessing
import subprocess
import glob
import os
import logging

dir_in = "NOT SET"
dir_out = "NOT SET"

def cellomics2tiff(file_in):
    head,tail = os.path.split(file_in)
    file_out = dir_out + "/" + tail.replace(".C01",".tif")

    cmd = ['bfconvert','-nogroup',file_in,file_out,'> /dev/null']
    print " ".join(cmd)
    #subprocess.call(cmd, shell=False)
    os.system(" ".join(cmd))

dir_in = sys.argv[1]
dir_out_root = sys.argv[2]
head,tail = os.path.split(dir_in)
dir_tmp = os.path.expanduser("~") + "/tmp/" + tail
#dir_out = dir_out_root + "/" + tail + "_converted"
dir_out = dir_tmp + "_converted"

print"Creating output directory " + dir_out
if not os.path.isdir(dir_out):
    os.makedirs(dir_out)
else:
    olds = glob.glob(dir_out + "/*.*")
    for old in olds:
        os.remove(old)

# Create log file
logging.basicConfig(filename=dir_out+'/cellomics2tiff.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

start_time = time.time()

# Copy data to the cluster
msg ="Copying data to " + dir_tmp + "..."
print msg
logging.info(msg)
os.system("rsync -r " + dir_in + "/ " + dir_tmp)
logging.info("Time elapsed: " + str(time.time() - start_time) + "s")

# Convert the data
start_time_convert = time.time()
msg = "Converting..."
print msg 
logging.info(msg)
pool = multiprocessing.Pool(None)
files = glob.glob(dir_tmp + "/*.C01")
r = pool.map(cellomics2tiff, files)
logging.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")

# Copy results outside the cluster
start_time_copy = time.time()
msg = "Copying results to " + dir_out_root
print msg
logging.info(msg)
os.system("rsync -r " + dir_out + " " + dir_out_root)
logging.info("Time elapsed: " + str(time.time() - start_time_copy) + "s")

logging.info("Total time elapsed: " + str(time.time() - start_time) + "s")
print "Done."

