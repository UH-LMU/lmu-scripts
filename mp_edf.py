#!/usr/bin/python
import math, sys, time
import multiprocessing
import subprocess
import glob
from optparse import OptionParser
import os
import logging

IMAGEJ = "/nfs/hajaalin/Software/Fiji.app/ImageJ-linux64"
EDF = "/nfs/hajaalin/Software/lmu-scripts/edf_process_headless.py"

# Create log file
logging.basicConfig(filename='edf.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

compute_output = "NOT_SET"

def edf(file_in):
    head,tail = os.path.split(file_in)
    file_out = compute_output + "/" + tail.replace(".tiff","_edf.tif")

    cmd = [IMAGEJ,EDF,"'"+file_in+"'","'"+file_out+"'",'> /dev/null']
    logging.info(" ".join(cmd))
    os.system(" ".join(cmd))


parser = OptionParser()
parser.add_option('-s','--staging', help='Staging input directory path or "AUTO"')
options,args = parser.parse_args()

dir_input = args[0]
dir_output_root = args[1]

input_root,tail = os.path.split(dir_input)
dir_output = os.path.join(dir_output_root,tail) + "_converted"

# start timer
start_time = time.time()


# check if output directory has data already
if os.path.isdir(dir_output):
    olds = glob.glob(dir_output + "/*_edf.tif")
    if len(olds) > 0:
        print "Output directory and converted files exists, aborting."
        sys.exit(1)
else:
    print "Creating output directory " + dir_output
    os.makedirs(dir_output)

staging = "NOT SET"
compute_output = dir_output
if options.staging:
    if options.staging == "AUTO":
        staging_root = os.path.expanduser("~") + "/tmp/" 
    else:
        staging_root = options.staging
    staging = os.path.join(staging_root,tail) 

    # check if data is already on the same device
    if os.stat(dir_input).st_dev == os.stat(staging).st_dev:
        print dir_input + " and " + staging + " are on same device. No need to transfer."
    else:
        msg ="Copying data to " + staging + "..."
        print msg
        logging.info(msg)
        cmd = "rsync -r '" + input_root + "/' " + staging
        logging.info(cmd)
        os.system(cmd)
        logging.info("Time elapsed: " + str(time.time() - start_time) + "s")

        dir_in = staging

    compute_output = staging + "_converted"


# Convert the data
start_time_convert = time.time()
msg = "Converting..."
print msg 
logging.info(msg)
pool = multiprocessing.Pool(None)
files = glob.glob(dir_input + "/*.tiff")
r = pool.map(edf, files)
logging.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")


# Copy results outside the cluster
if options.staging:
    start_time_copy = time.time()
    msg = "Copying results to " + dir_output_root
    print msg
    logging.info(msg)
    cmd = "rsync -r " + compute_output + " " + dir_output_root
    logging.info(cmd)
    os.system(cmd)
    logging.info("Time elapsed: " + str(time.time() - start_time_copy) + "s")

logging.info("Total time elapsed: " + str(time.time() - start_time) + "s")
print "Done."

