from ij import IJ
from ij import WindowManager as WM
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij.gui import MessageDialog
from ij.plugin import ImageCalculator
from java.awt import Color

import datetime
from math import ceil, log, sqrt
import os
import string
import sys
import time

from sys import path
from java.lang.System import getProperty
# extend the search path by $FIJI_ROOT/scripts/
path.append(getProperty('fiji.dir') + '/scripts')

WAIT = True
def waitUser(message):
	if WAIT:
		wait = WaitForUserDialog(message)
		wait.show()

# Check that we have an image
imp = IJ.getImage()
title = imp.getTitle()
title = title.replace(" ","_")
print "title", title


# Check that we have a ROI
roiObj = imp.getRoi()
if roiObj == None:
	print "Please select a rectangular ROI."
	sys.exit(1)
roi = roiObj.getBounds()

PIXELS_PER_PROCESSOR = 1000
N = int((roi.width * roi.height) / PIXELS_PER_PROCESSOR )


dialog = GenericDialog("ThreeB parallel setup")
dialog.addMessage("Microscope FWHM")
dialog.addNumericField("FWHM (nm)", 250,0,5,"")
dialog.addMessage("Pixel size")
dialog.addNumericField("Pixel (nm)", 100,0,5,"")
#dialog.addStringField("Name of job for high resolution scan", DefaultJobHigh)
dialog.addMessage("Number of processors")
dialog.addNumericField("N", N,0,5,"")
#dialog.addStringField("Name of job for high resolution scan", DefaultJobHigh)
#dialog.addMessage("Scans")
#dialog.addCheckbox("Perform low resolution scan?", 0)
dialog.setSize(400,600)
dialog.showDialog()

# Recover parameters from dialog box
#checkBoxes = dialog.getCheckboxes().elements()

FWHM_nm = float(dialog.getNextNumber())
pixel_nm = float(dialog.getNextNumber())
N = int(dialog.getNextNumber())
#LasafPort = dialog.getNextNumber()
#JobHigh = dialog.getNextString()

initial_spots = int(float(roi.width) * float(roi.height) / float(10) / float(N))

sigma = (FWHM_nm/pixel_nm) / (2*sqrt(2*log(2)))
blur_sigma = 0.1
blur_mu = log(sigma) + blur_sigma*blur_sigma

#LowScan = checkBoxes.nextElement().getState()

if dialog.wasCanceled():
	sys.exit(0)


# create timestamped directory for the run
t = time.time()
ft = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')
imgDir = IJ.getDirectory("image")
runDir = imgDir + title + "_3B_N" + str(N) + "_" + ft + "/"
print runDir
os.mkdir(runDir)

# create output directories
maskDir = runDir + "masks/"
os.mkdir(maskDir)
os.mkdir(runDir + "coordinates")
os.mkdir(runDir + "output")
os.mkdir(runDir + "results")

# prepare log file
setupLogName = runDir+"setup_parallel.log"
setupLog = open(setupLogName,"w")

# define mask grid
def isprime(n):
    """check if integer n is a prime"""
    # range starts with 2
    for x in xrange(2, n+1):
        if n % x == 0:
            return False
    return True

if isprime(N):
	print >> setupLog, "Prime number of processors, adding one..."
	N = N+1

nx = 1
ny = N
ratio_roi = float(roi.width) / float(roi.height)
ratio_diff_min = 99999999999
for i in range(1,N+1):
	for j in range(1,N+1):
		ratio_N = float(1) / float(j)
		ratio_diff = abs(ratio_N - ratio_roi)
		print ratio_diff
		if i*j == N and ratio_diff < ratio_diff_min:
			print "improved"
			ratio_diff_min = ratio_diff
			nx = int(i) 
			ny = int(j)

dx = ceil(float(roi.x)/float(nx))
dy = ceil(float(roi.y)/float(ny))

print >> setupLog, "ROI bounds: %d, %d, %d, %d" % (roi.x, roi.y, roi.width, roi.height)
print >> setupLog, "ROI size: %d" % (roi.width * roi.height)
print >> setupLog, "N processors: %d" % (N,)
print >> setupLog, "Mask grid (nx, ny): %d, %d" % (nx, ny)
print >> setupLog, "Mask size (dx, dy): %d, %d" % (dx, dy)
print >> setupLog, ""
print >> setupLog, "FWHM (nm): %f" % (FWHM_nm,)
print >> setupLog, "Pixel size (nm): %f" % (pixel_nm,)
print >> setupLog, "blur_mu: %f" % (blur_mu,)
print >> setupLog, "initial_spots: %d" % (initial_spots,)

# save maximum projection of the stack to show where the ROI was selected
dimensions = imp.getDimensions()
dataWidth = dimensions[0]
dataHeight = dimensions[1]
dataDepth = dimensions[2]
IJ.run(imp,"Z Project...","start=1 stop="+str(dataDepth) +" projection=[Max Intensity]")
maxProj = IJ.getImage()
maxProj.setRoi(roiObj,True)
maxProj.setImage(maxProj.flatten())
IJ.saveAs(maxProj,"jpg",maskDir + maxProj.getTitle())
maxProj.close()


print

# create masks
#IJ.setBackgroundColor(0,0,0)
#IJ.setForegroundColor(255,255,255)
#roiObj.setDefaultFillColor(Color(int(1),int(1),int(1)))

IJ.newImage("mask_small_sum", "8-bit", dataWidth, dataHeight, N)
sumSmall = IJ.getImage()

calc = ImageCalculator()
for i in range(0,nx):
	for j in range(0,ny):
		index = int(i*ny + j) + 1
		startx = roi.x + i*dx
		starty = roi.y + j*dy
		print >> setupLog, "mask %d: %d, %d" % (index, startx, starty)
		
		roiMask = Roi(startx,starty,roi.width,roi.height)
		mask = IJ.createImage("mask_small_" + str(index), "8-bit", dataWidth, dataHeight, 1)
		mask.setRoi(roiMask, False)
		IJ.run(mask,"Fill", "")
		#mask = IJ.getImage()
		#IJ.run(mask,"Convert to Mask", "")
		#mask = IJ.getImage()
		#IJ.run(mask,"Invert", "")
		IJ.saveAs(mask,"jpg",maskDir + mask.getTitle())

		sumSmall.getImageStack().setPixels(mask.getProcessor().getPixels(), index)
		
		mask.close()

		#waitUser("check...")

IJ.run(sumSmall,"Z Project...","start=1 stop="+str(N) +" projection=[Sum Slices]")
sumSmall = IJ.getImage()
IJ.saveAs(sumSmall,"jpg",maskDir + sumSmall.getTitle())

#sumSmall.close()
#sumLarge.close()

setupLog.close()

