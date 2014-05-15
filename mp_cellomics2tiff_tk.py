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
from utils import *

# use this on HCA workstation        

def cellomics2tiff((file_in,dir_out)):
    head,tail = os.path.split(file_in)
    file_out = dir_out + "/" + tail.replace(".C01",".tif")

    #logging.debug(" ".join(cmd))
    
    #subprocess.call(cmd, shell=False)
    #os.system(" ".join(cmd))

    if platform.system() == 'Linux':
        cmd = ['bfconvert','-nogroup',file_in,file_out,'> /dev/null']
        print " ".join(cmd)
        subprocess.call(cmd,  shell=False)
    else:
        cmd = ['bfconvert','-nogroup',file_in,file_out]
        print " ".join(cmd)
        subprocess.call(cmd,  shell=True)


class CellomicsConverter:

    def convert(self,inputDir, outputDir):

        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)
        else:
            olds = glob.glob(outputDir + "/*.*")
            for old in olds:
                os.remove(old)

        #logging.basicConfig(filename=outputDir+'/cellomics2tiff.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        #logging.basicConfig(level=logging.DEBUG)

        # recursively walk the directory and find all different field codes
        c01s = glob.glob(inputDir + "/*.C01")

        # temporary directory for conversions
        #tmpdir = tempfile.mkdtemp()

        # Convert the data
        start_time_convert = time.time()
        msg = "Converting..."
        print msg 
        #logging.info(msg)
        pool = multiprocessing.Pool(None)
        files = glob.glob(inputDir + "/*.C01")
        r = pool.map(cellomics2tiff, zip(files,repeat(outputDir)))
        #logging.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")
        print "Time elapsed: " + str(time.time() - start_time_convert) + "s"

        # remove temporary files
        #shutil.rmtree(tmpdir)


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
        inputdir = args[0]
        print inputdir

        # output directory
        head,tail = os.path.split(inputdir)
        outputRoot = head
        if options.output_root:
            outputRoot = options.output_root  
        outputDir = os.path.join(outputRoot, tail + "_tifs")
            
        converter.convert(inputDir, outputDir)
        
    # otherwise use Tk to get the info from user
    else:
        import Tkinter, Tkconstants, tkFileDialog
        root = Tkinter.Tk()
        Cellomics2TiffDialog(root,converter).pack()
        root.mainloop()


