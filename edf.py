import glob
import os.path

from ij import IJ, ImagePlus, ImageStack, WindowManager
from ij.io import DirectoryChooser

from edfgui import ExtendedDepthOfField, Parameters

dc = DirectoryChooser("Set input directory")
files = glob.glob(dc.getDirectory() + "/*.tiff")

dc = DirectoryChooser("Set output directory")
outputDir = dc.getDirectory()

# EDF parameters
params = Parameters()
params.setQualitySettings(params.QUALITY_HIGH)

for f in files:
    imp = ImagePlus(f)

    # output name
    head,tail = os.path.split(f)
    base,ext = os.path.splitext(tail)
    output = os.path.join(outputDir,base + "_edf.tif")
    print output

    # make all-in-focus image
    edf = ExtendedDepthOfField(imp,params)
    edf.process()

    # save output
    imp = WindowManager.getCurrentImage()
    IJ.saveAsTiff(imp,output)
    imp.close()

