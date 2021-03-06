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
import shutil
import string
import subprocess
import sys
import tempfile
import time
import Tkinter, Tkconstants, tkFileDialog

import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *

class Matrix2StacksDialog(Tkinter.Frame):

    def __init__(self, root, converter=None):

        self.converter = converter

        Tkinter.Frame.__init__(self, root)

        # options for buttons
        button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        self.DEFAULT_OUTPUTROOT = "OUTPUT ROOT DIRECTORY NOT SET"
        self.vin = StringVar()
        self.vin.set("INPUT DIRECTORY NOT SET")
        self.voutroot = StringVar()
        self.voutroot.set(self.DEFAULT_OUTPUTROOT)
        self.vout = StringVar()
        self.vout.set("OUTPUT DIRECTORY NOT SET")
        self.voutleaf = StringVar()
        self.vmask = StringVar()
        self.vmask.set('*')
        self.vwellcodes = IntVar()
        self.vfirstwell = StringVar()
        self.vfirstwell.set("A01")

        # define buttons
        Tkinter.Button(self, text='Select input directory', command=self.askinputdirectory).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vin).pack(**button_opt)
        Tkinter.Label(self, text='File filter (e.g. *J07*)').pack(**button_opt)
        Tkinter.Entry(self, textvariable=self.vmask).pack(**button_opt)
        Tkinter.Button(self, text='Select output root directory', command=self.askoutputdirectory).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.voutroot).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vout).pack(**button_opt)
        Tkinter.Label(self, text="Prepend well and field codes").pack()
        Tkinter.Checkbutton(self, text="Prepend well and field codes",variable=self.vwellcodes).pack()

        Tkinter.Label(self, text="First well").pack()
        Tkinter.Entry(self, textvariable=self.vfirstwell).pack()

        Tkinter.Button(self, text="Start conversion", command=self.startconversion).pack()


        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'Select directory'

    def askinputdirectory(self):

        """Returns a selected directoryname."""

        dirname = tkFileDialog.askdirectory(**self.dir_opt)
        head,tail = os.path.split(dirname)
        self.vin.set(dirname)

        if self.voutroot.get() == self.DEFAULT_OUTPUTROOT:
            self.voutroot.set(head)

        self.voutleaf.set(tail+ "_stacks")
        self.vout.set(self.voutroot.get() + "/" + self.voutleaf.get())

    def askoutputdirectory(self):

        """Returns a selected directoryname."""

        dirname = tkFileDialog.askdirectory(**self.dir_opt)
        self.voutroot.set(dirname)
        self.vout.set(self.voutroot.get() + "/" + self.voutleaf.get())

    def startconversion(self):
        print "Matrix2StacksDialog converting..."
        print self.vin.get()
        print self.vout.get()
        print self.vwellcodes.get()
        print self.vmask.get()
        print self.vfirstwell.get()

        if self.converter != None:
            self.converter.convert(self.vin.get(),self.vout.get(),self.vwellcodes.get(),self.vfirstwell.get(),self.vmask.get())

class MatrixUtils:
    rows = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    refirstwell = re.compile('([A-Z])([0-9]+)')
    rematrixwell = re.compile('U([0-9]+)--V([0-9]+)')
    rematrixfield = re.compile('X([0-9]+)--Y([0-9]+)')


    def wellcode(self,matrixname,firstwell='A01'):
        result = re.search(self.rematrixwell,matrixname)
        if result == None:
            raise(Error("Well code not found: " + matrixname))
        u = int(result.group(1))
        v = int(result.group(2))

        result = re.search(self.refirstwell,firstwell)
        if result == None:
            raise(Error("Bad well code: " + firstwell))
        offsetu = int(result.group(2))
        offsetv = self.rows.index(result.group(1))

        return self.rows[v+offsetv] + repr(u+offsetu).zfill(2)

    def fieldcode(self,matrixname):
        result = re.search(self.rematrixfield,matrixname)
        if result == None:
            raise(Error("Field code not found: " + matrixname))
        x = int(result.group(1))
        y = int(result.group(2))

        return str(x)+str(y)

def convertField((f, config)):
    inputDir = config[0]
    tmpDir = config[1]
    outputDir = config[2]
    addWell = config[3]
    firstWell = config[4]

    # define output file name
    outputFile = f
    if addWell:
        mu = MatrixUtils()
        outputFile = mu.wellcode(f,firstWell) + '_' + mu.fieldcode(f) + '_' + f
    outputFile =  outputDir + "/" + outputFile + ".tif"

    # find images belonging to this field
    tifs = set()
    for root, dirnames, filenames in os.walk(inputDir):
      for filename in fnmatch.filter(filenames, "*" + f + "*.tif"):
          tifs.add(os.path.join(root,filename))

    # find different channels, slices and timepoints that are recorded for this field,
    # store filenames in memory
    reOME = re.compile('image--L([0-9]+)--S([0-9]+)--U([0-9]+)--V([0-9]+)--J([0-9]+)--E([0-9]+)--O([0-9]+)--X([0-9]+)--Y([0-9]+)--T([0-9]+)--Z([0-9]+)--C([0-9]+).ome.tif')
    reSlice = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+--T[0-9]+--Z[0-9]+')

    _hyperstack = {}
    for t in tifs:
        print "tif " + t
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
            tmpfile = os.path.join(tmpDir, reSlice.search(slicefile).group(0) + '.tif')

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




class Matrix2StacksConverter:

    def convert(self,inputDir, outputDir, addWell="False", firstWell="A01", mask='*'):
        # regexp that defines a Matrix Screener field.
        reField = re.compile('S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+')

        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)
        else:
            olds = glob.glob(outputDir + "/*.*")
            for old in olds:
                os.remove(old)

        #logging.basicConfig(filename=stackDir+'/bfconvertMatrixScreener.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

        # recursively walk the directory and find all different field codes
        fields = set()
        for root, dirnames, filenames in os.walk(inputDir):
          for filename in fnmatch.filter(filenames, mask + '.tif'):
              result = reField.search(filename)
              fieldname = result.group(0)
              fields.add(fieldname)

        # temporary directory for conversions
        tmpDir = tempfile.mkdtemp(dir="/matrix-data/tmp")

        config = [inputDir,tmpDir,outputDir,addWell,firstWell]

        # loop over all wells
        # for f in fields:
        #     convertField(f, config)

        # Convert the data
        start_time_convert = time.time()
        logging.info("Converting...")
        pool = multiprocessing.Pool(None)
#        files = glob.glob(inputDir + "/*.C01")

        # http://stackoverflow.com/questions/8521883/multiprocessing-pool-map-and-function-with-two-arguments
        r = pool.map(convertField, zip(fields,repeat(config)))
        pool.close()
        pool.join()
        logging.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")

        # remove temporary files
        #shutil.rmtree(tmpDir)



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
        inputDir = args[0]
        print inputDir

        # output directory
        head,tail = os.path.split(inputDir)
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
