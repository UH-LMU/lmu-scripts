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

from mdb_export import mdb_export
from utils import *

cutils = CellomicsUtils()

def cellomics2tiff((file_in,dir_out)):
    """Converts individual C01 file to TIF using bfconvert."""
    
    file_out = cutils.getTifPath(file_in,dir_out)

    # don't repeat conversion if converted file exists
    # and is newer than the original data
    if os.path.isfile(file_out) \
       and os.stat(file_out).st_mtime > os.stat(file_in).st_mtime:
        return

    if platform.system() == 'Linux':
        #cmd = ['bfconvert','-nogroup',file_in,file_out,'> /dev/null']
        #cmd = ['/opt/bftools/bfconvert','-nogroup',file_in,file_out,']
        #print " ".join(cmd)
        #FNULL = open(os.devnull,'w')
        #subprocess.call(cmd,  stdout=FNULL, shell=False)
        #FNULL.close()
        cmd = '/opt/bftools/bfconvert -overwrite -nogroup %s %s > /dev/null'%(file_in,file_out)
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
        print "mp_cellomics2tiff:","INPUT:", inputDir
        print "mp_cellomics2tiff:","OUTPUT:", outputDir

        # input image files
        c01s = glob.glob(inputDir + "/*.C01")

        if os.path.isdir(outputDir):
            # check if entire dataset is already converted
            if cutils.isDatasetConverted(inputDir,outputDir):
                logfile = open(os.path.join(outputDir,'cellomics2tiff_error.log'),'w')
                msg = "Seems that data was converted already, stopping."
                print >> logfile, msg
                print "mp_cellomics2tiff:",msg
                logfile.close()
                return
        else:
            os.makedirs(outputDir)

        metadataDir = os.path.join(outputDir,"metadata")
        if not os.path.isdir(metadataDir):
            os.makedirs(metadataDir)
            
        logging.basicConfig(filename=outputDir+'/cellomics2tiff.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

        # convert the metadata in MS Access files to CSV             
        msg = "Converting metadata to ", metadataDir
        print "mp_cellomics2tiff:",msg 
        mdbs = glob.glob(inputDir + "/*.MDB")
        mdbs.extend(glob.glob(inputDir + "/*.mdb"))
        for mdb in mdbs:
            print "MDB:",mdb
            mdb_export(mdb, metadataDir)

        # Convert the data
        start_time_convert = time.time()
        msg = "Converting..."
        print "mp_cellomics2tiff:",msg 
        logging.info(msg)
        pool = multiprocessing.Pool(None)
        files = glob.glob(inputDir + "/*.C01")

        # http://stackoverflow.com/questions/8521883/multiprocessing-pool-map-and-function-with-two-arguments
        r = pool.map(cellomics2tiff, zip(files,repeat(outputDir)))
        msg = "Time elapsed: " + str(time.time() - start_time_convert) + "s"
        print "mp_cellomics2tiff:",msg
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
        from dialogs import Cellomics2TiffDialog

        root = Tkinter.Tk()
        Cellomics2TiffDialog(root,converter).pack()
        root.mainloop()


