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

        

class Matrix2StacksConverter:

    def convert(self,inputDir, outputDir, add_well="False", firstwell="A01", mask='*'):
        # regexp that defines a Matrix Screener field.
        reOME = re.compile('image--L([0-9]+)--S([0-9]+)--U([0-9]+)--V([0-9]+)--J([0-9]+)--E([0-9]+)--O([0-9]+)--X([0-9]+)--Y([0-9]+)--T([0-9]+)--Z([0-9]+)--C([0-9]+).ome.tif')
        reSlice = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+--T[0-9]+--Z[0-9]+')
        reField = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+')
        reExp = re.compile('.*experiment--[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]')

        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)
        else:
            olds = glob.glob(outputDir + "/*.*")
            for old in olds:
                os.remove(old)

        abc = AbcIndex()
        mu = MatrixUtils()

        #logging.basicConfig(filename=stackDir+'/bfconvertMatrixScreener.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

        # recursively walk the directory and find all different field codes
        fields = set()
        for root, dirnames, filenames in os.walk(inputDir):
          for filename in fnmatch.filter(filenames, mask + '.tif'):
              result = reField.search(filename)
              fieldname = result.group(0)
              fields.add(root + "/" + fieldname)

        # temporary directory for conversions
        tmpdir = tempfile.mkdtemp()

        # loop over all wells
        for f in fields:
            # define output file name
            head,tail = os.path.split(f)
            outputFile =  outputDir + "/" + tail + ".tif"
            #if add_abc:
             #   outputFile = outputFile.replace('image',  'image_'+abc.next())
            if add_well:
                outputFile = outputFile.replace('image',  'image_'+mu.wellcode(outputFile,firstwell) + '_' + mu.fieldcode(outputFile))

            # find images belonging to this field
            tifs = glob.glob(f + "*.ome.tif")

            # find different channels, slices and timepoints that are recorded for this field,
            # store filenames in memory
            _hyperstack = {}
            for t in tifs:
                result = reOME.search(t)
                timepointId = result.group(10)
                sliceId = result.group(11)
                channelId = result.group(12)

                # the hyperstack contains all timepoint
                if not _hyperstack.has_key(timepointId):
                    _hyperstack[timepointId] = {}
                _timepoint = _hyperstack[timepointId]

                # a timepoint contains all z-slices
                if not _timepoint.has_key(sliceId):
                    _timepoint[sliceId] = {}
                _slice = _timepoint[sliceId]

                # a slice contains all channels
                _slice[channelId] = t
                #_slice.append(t)

            # command to combine images of a field
            cmd_field = ['imgcnv','-o',outputFile,'-t','ome-tiff','-geometry','%d,%d'%(len(_timepoint),len(_hyperstack))]

            # loop over all timepoints
            for t in sorted(_hyperstack.keys()):
                _timepoint = _hyperstack[t]

                # loop over all slices
                for z in sorted(_timepoint.keys()):
                    logging.debug("Field " + f)        
                    logging.debug("Timepoint " + t)
                    logging.debug("Z-slice " + z)        
                    _slice = _timepoint[z]

                    channels = sorted(_slice.keys())

                    # use the part without the channel code as the file name
                    slicefile = _slice[channels[0]]#_slice[0]
                    tmpfile = tmpdir + '/' + reSlice.search(slicefile).group(0) + '.tif'

                    # command to combine channels  
                    cmd = ['imgcnv','-o',tmpfile,'-t','ome-tiff']

                    c = channels.pop(0)
                    cmd.extend(['-i',_slice[c]])
                    for c in channels:
                        cmd.extend(['-c',_slice[c]])
                        
                    logging.debug(" ".join(cmd))

                    if platform.system() == 'Linux':
                        subprocess.call(cmd,  shell=False)
                    else:
                        subprocess.call(cmd,  shell=True)

                    # update the command that will combine all images of a field
                    cmd_field.extend(['-i',tmpfile])
                    

            logging.debug(" ".join(cmd_field))
            if platform.system() == 'Linux':
                subprocess.call(cmd_field,  shell=False)
            else:
                subprocess.call(cmd_field,  shell=True)

        # remove temporary files
        shutil.rmtree(tmpdir)
        



if __name__=='__main__':

    usage ="""%prog [options] input_directory

    Convert MatrixScreener data to stacks, one multicolor stack per field. 
    Run '%prog -h' for options.
    """

    parser = OptionParser(usage=usage)
    parser.add_option('-n', '--dryrun', action="store_true", default=False, help="Print actions but do not execute.")
    parser.add_option('-v', '--verbose', action="store_true", default=False, help="")
    parser.add_option('-a', '--add_abc', action="store_true", default=False, help="")
    parser.add_option('--add_well', action="store_true", default=False, help="")
    parser.add_option('--first_well', default="A01", help="First well that was imaged.")
    parser.add_option('-d', '--output_root', help="Directory where the stacks will be stored.")
    parser.add_option('-m', '--mask', default="*", help="Filename filter, e.g. *J07*.")
    options, args = parser.parse_args()
    
    converter = Matrix2StacksConverter()

    # use command line arguments, if they were given
    if len(args) > 0:
        inputdir = args[0]
        print inputdir

        # output directory
        head,tail = os.path.split(inputdir)
        outputRoot = head
        if options.output_root:
            outputRoot = options.output_root  
        outputDir = os.path.join(outputRoot, tail + "_stacks")
            
        converter.convert(inputDir, outputDir, options.add_well, options.first_well, options.mask)
        
    # otherwise use Tk to get the info from user
    else:
        root = Tkinter.Tk()
        Matrix2StacksDialog(root,converter).pack()
        root.mainloop()



