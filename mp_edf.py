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

def edf(file_in,dir_out):
    head,tail = os.path.split(file_in)
    file_out = dir_out + "/" + tail.replace(".tiff","_edf.tif")

    cmd = [IMAGEJ,EDF,"'"+file_in+"'","'"+file_out+"'",'> /dev/null']
    print " ".join(cmd)
    #subprocess.call(cmd, shell=False)
    os.system(" ".join(cmd))


parser = OptionParser()
parser.add_option('-i','--staging_input', help='Staging input directory path or "AUTO"')
options,args = parser.parse_args()

dir_input = args[0]
dir_output_root = args[1]

input_root,tail = os.path.split(dir_input)
dir_output = os.path.join(dir_out_root,tail) + "_converted"

# start timer
start_time = time.time()

# Create log file
logging.basicConfig(filename=dir_out+'/edf.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

# check if output directory has data already
if os.path.isdir(dir_output):
    olds = glob.glob(dir_output + "/*.edf.tif")
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
        #os.system(cmd)
        logging.info("Time elapsed: " + str(time.time() - start_time) + "s")

        dir_in = staging

    compute_output = staging + "_converted"


# Convert the data
start_time_convert = time.time()
msg = "Converting..."
print msg 
logging.info(msg)
pool = multiprocessing.Pool(None)
files = glob.glob(dir_in + "/*.tiff")
r = pool.map(edf, files, compute_output)
logging.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")


# Copy results outside the cluster
if options.staging:
    start_time_copy = time.time()
    msg = "Copying results to " + dir_out_root
    print msg
    logging.info(msg)
    cmd = "rsync -r " + compute_output + " " + dir_out_root
    logging.info(cmd)
    #os.system(cmd)
    logging.info("Time elapsed: " + str(time.time() - start_time_copy) + "s")

logging.info("Total time elapsed: " + str(time.time() - start_time) + "s")
print "Done."

