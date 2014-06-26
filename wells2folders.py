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
import time
import tempfile
import shutil
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *

from mdb_export import mdb_export
from utils import *

class Wells2FoldersDialog(Tkinter.Frame):

    def __init__(self, root, converter=None):

        self.converter = converter

        Tkinter.Frame.__init__(self, root)

        # options for buttons
        button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        self.vin = StringVar()
        self.vin.set("INPUT DIRECTORY NOT SET")

        # define buttons
        Tkinter.Button(self, text='Select input directory', command=self.askinputdirectory).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vin).pack(**button_opt)

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'Select directory'

        Tkinter.Button(self, text="Sort by wells", command=self.startconversion).pack()

    def askinputdirectory(self):

        """Returns a selected directoryname."""

        dirname = tkFileDialog.askdirectory(**self.dir_opt)
        head,tail = os.path.split(dirname)
        self.vin.set(dirname)

    def startconversion(self):
        print "Matrix2StacksDialog converting..."
        print self.vin.get()
        
        if self.converter != None:
            self.converter.convert(self.vin.get())



class Wells2Folders:
    """Rearranges well-plate data."""

    reImage = re.compile('.*_[0-9]{12}_([A-Z][0-9]{2})f.*tif')
    def convert(self,inputDir):
        print "INPUT: " + inputDir

        tifs = glob.glob(inputDir + "/*.tif")
        for tif in tifs:
            print "TIF:", tif
            well = re.search(self.reImage,tif).groups()[0]
            print "WELL:",well

            wellDir = os.path.join(inputDir,well)
            print "WELLDIR:",wellDir
            if not os.path.isdir(wellDir):
                os.makedirs(wellDir)
            #old = os.path.join(inputDir,tif)
            #new = os.path.join(wellDir,tif)
            new = wellDir + "/" + tif
            #print "OLD:",old
            #print "NEW:",new
            shutil.move(tif, wellDir)

            

if __name__=='__main__':

    usage ="""%prog [options] input_directory

    Rearrange well-plate data to folder per well. 
    Run '%prog -h' for options.
    """

    parser = OptionParser(usage=usage)
    options, args = parser.parse_args()
    
    converter = Wells2Folders()

    # use command line arguments, if they were given
    if len(args) > 0:
        inputDir = args[0]
       
        converter.convert(inputDir)
        
    # otherwise use Tk to get the info from user
    else:
        root = Tkinter.Tk()
        Wells2FoldersDialog(root,converter).pack()
        root.mainloop()

