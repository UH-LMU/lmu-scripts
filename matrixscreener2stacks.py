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

class AbcIndex:
    
    def __init__(self):
        self.i = 0
        self.j = 0
        self.k = 0
        self.abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', 'Z']
        
    def next(self):
        next_out = self.abc[self.i] + self.abc[self.j] + self.abc[self.k]
        
        self.k = self.k+1
        if self.k > len(self.abc) -1:
            self.k = 0
            self.j = self.j + 1

        if self.j > len(self.abc) -1:
            self.j = 0
            self.i = self.i + 1
            
        if self.i > len(self.abc) -1:
            return False
            
        return next_out


usage ="""%prog [options] target

Convert MatrixScreener data to stacks, one multicolor stack per field. 
Run '%prog -h' for options.
"""

parser = OptionParser(usage=usage)
parser.add_option('-n', '--dryrun', action="store_true", default=False, help="Print actions but do not execute.")
parser.add_option('-v', '--verbose', action="store_true", default=False, help="")
parser.add_option('-a', '--add_abc', action="store_true", default=False, help="")
parser.add_option('-d', '--output_root', help="Directory where the stacks will be stored.")
options, args = parser.parse_args()

# use command line arguments, if they were given
if len(args) > 0:
    filename = args[0]
    print filename
    add_abc = options.add_abc
# otherwise use Tk to get the info from user
else:
    from Tkinter import Tk
    from tkFileDialog import askopenfilename

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    
    add_abc = False
    master = Tk()
    var = IntVar()
    c = Checkbutton(master, text="Add 3-letter code to stack names", variable=var)
    c.pack()
    if var.get() == 1:
        add_abc = True


abc = AbcIndex()
#for i in range(0, 100):
#    print abc.next()

# regexp that defines a Matrix Screener field.
reOME = re.compile('image--L([0-9]+)--S([0-9]+)--U([0-9]+)--V([0-9]+)--J([0-9]+)--E([0-9]+)--O([0-9]+)--X([0-9]+)--Y([0-9]+)--T([0-9]+)--Z([0-9]+)--C([0-9]+).ome.tif')
reSlice = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+--T[0-9]+--Z[0-9]+')
reField = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+')
reExp = re.compile('.*experiment--[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]')

result = reExp.search(filename)
experiment = result.group(0)
head,tail = os.path.split(experiment)

outputRoot = head
if options.output_root:
    outputRoot = options.output_root  
outputDir = os.path.join(outputRoot, tail + "_stacks")

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
for root, dirnames, filenames in os.walk(experiment):
  for filename in fnmatch.filter(filenames, '*.tif'):
      result = reField.search(filename)
      fieldname = result.group(0)
      fields.add(root + "/" + fieldname)

# temporary directory for conversions
tmpdir = tempfile.mkdtemp()

# loop over all wells
for f in fields:
    # define output file name
    head,tail = os.path.split(f)
    #tif = tifs[0]
    #result = reField.search(tif)
    #outputFile =  outputDir + "/" + result.group(0) + ".tif"
    outputFile =  outputDir + "/" + tail + ".tif"
    if add_abc:
        outputFile = outputFile.replace('image',  'image_'+abc.next())

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
            _timepoint[sliceId] = []
        _slice = _timepoint[sliceId]

        # a slice contains all channels
        #_slice.append(root + "/" + filename)
        _slice.append(t)


    # loop over all timepoints
    cmd_field = ['imgcnv','-o',outputFile,'-t','ome-tiff','-geometry','%d,%d'%(len(_timepoint),len(_hyperstack))]

    for t in _hyperstack.keys():
        _timepoint = _hyperstack[t]

        # loop over all slices
        for z in _timepoint.keys():
            logging.debug("Field " + f)        
            logging.debug("Timepoint " + t)
            logging.debug("Z-slice " + z)        
            _slice = _timepoint[z]

            # use the part without the channel code as the file name
            slicefile = _slice[0]
            tmpfile = tmpdir + '/' + reSlice.search(slicefile).group(0) + '.tif'

            # command to combine channels  
            cmd = ['imgcnv','-o',tmpfile,'-t','ome-tiff']
            c = _slice.pop(0)
            cmd.extend(['-i',c])
            for c in _slice:
                cmd.extend(['-c',c])
                
            logging.debug(" ".join(cmd))

            if platform.system() == 'Linux':
                subprocess.call(cmd,  shell=False)
            else:
                subprocess.call(cmd,  shell=True)

            # update the command that will combine all slices
            cmd_field.extend(['-i',tmpfile])
            

    if platform.system() == 'Linux':
        subprocess.call(cmd_field,  shell=False)
    else:
        subprocess.call(cmd_field,  shell=True)

# remove temporary files
shutil.rmtree(tmpdir)
    
