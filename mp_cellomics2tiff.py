#!/usr/bin/env python
import fnmatch
import glob
from itertools import repeat
import logging
import multiprocessing
from optparse import OptionParser
import os
import os.path
import platform
import re
import string
import subprocess
import sys
import time
import tempfile
import shutil

from dialogs import *
from mdb_export import mdb_export
from utils import *

def cellomics2tiff((file_in,dir_out)):
    """Converts individual C01 file to TIF using bfconvert."""
    
    head,tail = os.path.split(file_in)
    file_out = dir_out + "/" + tail.replace(".C01",".tif")

    #logging.debug(" ".join(cmd))
    
    #subprocess.call(cmd, shell=False)
    #os.system(" ".join(cmd))

    if platform.system() == 'Linux':
        #cmd = ['bfconvert','-nogroup',file_in,file_out,'> /dev/null']
        #cmd = ['/opt/bftools/bfconvert','-nogroup',file_in,file_out,']
        #print " ".join(cmd)
        #FNULL = open(os.devnull,'w')
        #subprocess.call(cmd,  stdout=FNULL, shell=False)
        #FNULL.close()
        cmd = '/opt/bftools/bfconvert -nogroup %s %s > /dev/null'%(file_in,file_out)
        #print cmd
        os.system(cmd)
    else:
        cmd = ['bfconvert','-nogroup',file_in,file_out]
        print " ".join(cmd)
        subprocess.call(cmd,  shell=True)


class CellomicsConverter:
    """Converts C01 files in parallel."""
    
    def convert(self,inputDir, outputDir):
        """Converts a folder of C01 files."""
        print "INPUT: " + inputDir
        print "OUTPUT: " + outputDir

        # check if dataset is already converted
        if os.path.isdir(outputDir):
            tifs = glob.glob(outputDir + "/*.tif")
            if len(tifs) > 0:
                logfile = open(os.path.join(outputDir,'cellomics2tiff_error.log'),'w')
                msg = "Seems that data was converted already, stopping."
                print >> logfile, msg
                print msg
                logfile.close()
                return
        else:
            os.makedirs(outputDir)

        os.makedirs(os.path.join(outputDir,"metadata"))
        logging.basicConfig(filename=outputDir+'/cellomics2tiff.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

        # convert the metadata in MS Access files to CSV             
        mdbs = glob.glob(inputDir + "/*.MDB")
        for mdb in mdbs:
            mdb_export(mdb, os.path.join(outputDir,"metadata"))


        # recursively walk the directory and find all different field codes
        c01s = glob.glob(inputDir + "/*.C01")

        # Convert the data
        start_time_convert = time.time()
        msg = "Converting..."
        print msg 
        logging.info(msg)
        pool = multiprocessing.Pool(None)
        files = glob.glob(inputDir + "/*.C01")

        # http://stackoverflow.com/questions/8521883/multiprocessing-pool-map-and-function-with-two-arguments
        r = pool.map(cellomics2tiff, zip(files,repeat(outputDir)))
        msg = "Time elapsed: " + str(time.time() - start_time_convert) + "s"
        print msg
        logging.info(msg)



if __name__=='__main__':

    usage ="""%prog [options] input_directory

    Convert MatrixScreener data to stacks, one multicolor stack per field. 
    Run '%prog -h' for options.
    """

    parser = OptionParser(usage=usage)
    parser.add_option('-n', '--dryrun', action="store_true", default=False, help="Print actions but do not execute.")
    parser.add_option('-v', '--verbose', action="store_true", default=False, help="")
    parser.add_option('-d', '--output_root', help="Directory where the stacks will be stored.")
    options, args = parser.parse_args()
    
    converter = CellomicsConverter()

    # use command line arguments, if they were given
    if len(args) > 0:
        inputDir = args[0]
       
        # output directory
        head,tail = os.path.split(inputDir)
        outputRoot = head
        if options.output_root:
            outputRoot = options.output_root  
        outputDir = os.path.join(outputRoot, tail + "_converted")
            
        converter.convert(inputDir, outputDir)
        
    # otherwise use Tk to get the info from user
    else:
        import Tkinter, Tkconstants, tkFileDialog
        root = Tkinter.Tk()
        Cellomics2TiffDialog(root,converter).pack()
        root.mainloop()


