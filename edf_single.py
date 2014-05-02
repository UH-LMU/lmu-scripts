import glob
import os.path
import sys

from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser

from edfgui import ExtendedDepthOfField, Parameters

file_in = sys.argv[1]
file_out = sys.argv[2]

# EDF parameters
params = Parameters()
params.setQualitySettings(params.QUALITY_HIGH)

# read input image
imp = ImagePlus(file_in)

# make all-in-focus image
edf = ExtendedDepthOfField(imp,params)
edf.process()

# save output
imp = WindowManager.getCurrentImage()
IJ.saveAsTiff(imp,file_out)
imp.close()

