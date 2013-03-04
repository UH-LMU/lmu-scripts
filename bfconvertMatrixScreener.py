import glob
import logging
import os
import os.path
import re
import string
import subprocess
import sys

from Tkinter import Tk
from tkFileDialog import askopenfilename

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

abc = AbcIndex()
#for i in range(0, 100):
#    print abc.next()
    
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
#filename = sys.argv[1]

# regexp that defines a Matrix Screener OME Tiff file.
reOME = re.compile('image--L([0-9]+)--S([0-9]+)--U([0-9]+)--V([0-9]+)--J([0-9]+)--E([0-9]+)--O([0-9]+)--X([0-9]+)--Y([0-9]+)--T([0-9]+)--Z([0-9]+)--C([0-9]+).ome.tif')
reStack = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+--T[0-9]+')
reExp = re.compile('.*experiment--[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]')

result = reExp.search(filename)
experiment = result.group(0)
print experiment

stackDir = experiment + "_stacks"
if not os.path.isdir(stackDir):
    os.makedirs(stackDir)
else:
    olds = glob.glob(stackDir + "/*.*")
    for old in olds:
        os.remove(old)
        
logging.basicConfig(filename=stackDir+'/bfconvertMatrixScreener.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)

# loop over all wells
wells = glob.glob(experiment + "/slide--S00/chamber--*")
for w in wells:
    logging.debug( "Well " + w)

# loop over all fields
    fields = glob.glob(w + "/field--*")
    for f in fields:
        logging.debug("Field " + f)        

        tifs = glob.glob(f + "/*.ome.tif")
        tif = tifs[0]
        logging.debug("start conversion with " + tif)

        result = reStack.search(tif)
        stackFile =  stackDir + "/" + result.group(0) + ".tif"
        stackFile = stackFile.replace('image',  'image_'+abc.next())
        logging.debug("stack name " +  stackFile)
        
        cmd = ['bfconvert', '-overwrite', '-merge', '-stitch', tif, stackFile]
        subprocess.call(cmd,  shell=True)
