import glob
import os.path
import sys

from ij import IJ, ImagePlus, ImageStack, WindowManager

from edf import EdfComplexWavelets, PostProcessing, Tools
from edfgui import ExtendedDepthOfField, Parameters
from imageware import Builder, ImageWare

file_in = sys.argv[1]
file_out = sys.argv[2]

print file_in
print file_out

# 
REAL_WAVELETS = 2
COMPLEX_WAVELETS = 3

# EDF parameters
params = Parameters()
params.setQualitySettings(params.QUALITY_HIGH)
params.nScales = 10

# read input image
imp = ImagePlus(file_in)
print imp

#
# this is a reproduction of method "process" in edfgui.ExtendedDepthOfField.
#
def process():
    isExtended = False
    waveletMethod = params.edfMethod == REAL_WAVELETS \
        or params.edfMethod == COMPLEX_WAVELETS

    stackConverted = None
    impConverted = None
    impBW = imp

    if params.color:
        print "Color support not ready yet"
        sys.exit(1)

    imageStack = Builder.wrap(impBW)

    scaleAndSizes = []
    nx = imageStack.getWidth()
    ny = imageStack.getHeight()

    if waveletMethod:
        if not Tools.isPowerOf2(nx) or not Tools.isPowerOf2(ny):
            scaleAndSizes = Tools.computeScaleAndPowerTwoSize(nx,ny)
            imageStack = Tools.extend(imageStack, scaleAndSizes[1], scaleAndSizes[2])
            isExtended = True


    ima = []

    if params.edfMethod == COMPLEX_WAVELETS:
        edf = EdfComplexWavelets(params.daubechielength,params.nScales,params.subBandCC,params.majCC)
        ima = edf.process(imageStack)
    else:
        print "Method not supported yet, sorry!"
        sys.exit(1)

    # crop to original images    
    if waveletMethod and isExtended:
        imageStack = Tools.crop(imageStack, nx, ny)
        ima[0] = Tools.crop(ima[0],nx,ny)
        ima[1] = Tools.crop(ima[0],nx,ny)

    if params.reassignment:
        ima[1] = PostProcessing.reassignment(ima[0],imageStack)

    if params.doDenoising and not waveletMethod:
        print "option not supported: doDenoising"
        sys.exit(1)

    impComposite = ImagePlus("Output", ima[0].buildImageStack())    
    return impComposite


# process input
output = process()

# save output
IJ.saveAsTiff(output,file_out)

# close images
output.close()
imp.close()

