#!/usr/bin/env python
import fnmatch
import glob
import logging
from optparse import OptionParser
import os
import os.path
import platform
import re
import string
import subprocess
import sys
import tempfile
import Tkinter, Tkconstants, tkFileDialog
import shutil

from dialogs import *
from utils import *

        

class CellomicsConverter:

    def convert(self,inputDir, outputDir):

        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)
        else:
            olds = glob.glob(outputDir + "/*.*")
            for old in olds:
                os.remove(old)

        logging.basicConfig(filename=outputDir+'/cellomics2tiff.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        #logging.basicConfig(level=logging.DEBUG)

        # recursively walk the directory and find all different field codes
        c01s = glob.glob(inputDir + "/*.C01")

        # temporary directory for conversions
        #tmpdir = tempfile.mkdtemp()

        # loop over all wells
        for f in c01s:
            # define output file name
            head,tail = os.path.split(f)
            outputFile =  outputDir + "/" + tail.replace("C01","tif")

            # command to combine images of a field
            cmd_field = ['bfconvert','-nogroup',f,outputFile]                    
            logging.debug(" ".join(cmd_field))
            
            if platform.system() == 'Linux':
                subprocess.call(cmd_field,  shell=False)
            else:
                subprocess.call(cmd_field,  shell=True)

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
        root = Tkinter.Tk()
        Cellomics2TiffDialog(root,converter).pack()
        root.mainloop()



