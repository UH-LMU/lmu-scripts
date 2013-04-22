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
dialog.addMessage("Root directory")
dialog.addStringField("Root", "$WRKDIR/3B/runs/")
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
root = dialog.getNextString()

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
runDir = title + "_3B_N" + str(N) + "_" + ft + "/"
print imgDir + runDir
os.mkdir(imgDir + runDir)

# create output directories
maskDir = imgDir + runDir + "masks/"
os.mkdir(maskDir)
os.mkdir(imgDir + runDir + "coordinates")
os.mkdir(imgDir + runDir + "output")
os.mkdir(imgDir + runDir + "results")

# prepare log file
setupLogName = imgDir + runDir+"setup_parallel.log"
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
		ratio_N = float(i) / float(j)
		ratio_diff = abs(ratio_N - ratio_roi)
		if i*j == N and ratio_diff < ratio_diff_min:
			print i, j, i*j, ratio_roi, ratio_N, ratio_diff
			#print "improved"
			ratio_diff_min = ratio_diff
			nx = int(i) 
			ny = int(j)

dx = ceil(float(roi.width)/float(nx))
dy = ceil(float(roi.height)/float(ny))

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
IJ.setBackgroundColor(0,0,0)
IJ.setForegroundColor(50,50,50)
#roiObj.setDefaultFillColor(Color(int(1),int(1),int(1)))
#roiObj.setDefaultFillColor(Color(int(0),int(0),int(0)))


IJ.newImage("mask_small_sum", "8-bit", dataWidth, dataHeight, N)
sumSmall = IJ.getImage()
for i in xrange(1, sumSmall.getStack().getSize() + 1):
  # ip is the ImageProcessor for one stack slice
  ip = sumSmall.getStack().getProcessor(i)
  ip.multiply(0)
  
IJ.newImage("mask_large_sum", "8-bit", dataWidth, dataHeight, N)
sumLarge = IJ.getImage()
for i in xrange(1, sumLarge.getStack().getSize() + 1):
  # ip is the ImageProcessor for one stack slice
  ip = sumLarge.getStack().getProcessor(i)
  ip.multiply(0)
 

calc = ImageCalculator()
for i in range(0,nx):
	for j in range(0,ny):
		index = int(i*ny + j) + 1
		startx = roi.x + i*dx
		starty = roi.y + j*dy
		print >> setupLog, "mask %d: %d, %d, %d, %d" % (index, startx, starty,dx,dy)
		
		maskRoi = Roi(startx,starty,dx,dy)
		mask = IJ.createImage("mask_small_" + str(index), "8-bit", dataWidth, dataHeight, 1)

		# set all pixels to 0
		mask.getProcessor().multiply(0)
		mask.setRoi(maskRoi, True)
		mask.getProcessor().setValue(50)
		mask.getProcessor().fill(maskRoi)

		IJ.saveAs(mask,"jpg",maskDir + mask.getTitle())

		#print "set sum small slice index", sumSmall.getImageStack().getSize(), index
		sumSmall.getImageStack().setPixels(mask.getProcessor().getPixelsCopy(), index)

		#mask.getProcessor().dilate()
		#mask.getProcessor().fill(maskRoi)
		#mask.getProcessor().dilate()
		#mask.getProcessor().fill(maskRoi)
		#mask.getProcessor().dilate()
		#mask.getProcessor().fill(maskRoi)
		mask.getProcessor().erode()
		mask.getProcessor().erode()
		mask.getProcessor().erode()
		
		IJ.saveAs(mask,"jpg",maskDir + "mask_large_" + str(index))
		
		sumLarge.getImageStack().setPixels(mask.getProcessor().getPixelsCopy(), index)
		
		mask.close()

		#waitUser("check...")

IJ.run(sumSmall,"Z Project...","start=1 stop="+str(N) +" projection=[Sum Slices]")
sumSmallProj = IJ.getImage()
IJ.saveAs(sumSmallProj,"jpg",maskDir + sumSmall.getTitle())

IJ.run(sumLarge,"Z Project...","start=1 stop="+str(N) +" projection=[Sum Slices]")
sumLargeProj = IJ.getImage()
IJ.saveAs(sumLargeProj,"jpg",maskDir + sumLarge.getTitle())

sumSmall.close()
sumSmallProj.close()
sumLarge.close()
sumLargeProj.close()

setupLog.close()

# prepare batch file
batchName = imgDir + runDir+"batch_vuori.sh"
batch = open(batchName,"w")
print >> batch, "#!/bin/csh"
print >> batch, "#SBATCH -J 3B-"+ ft
print >> batch, "#SBATCH -e output/my_output_err_%j"
print >> batch, "#SBATCH -o output/my_output_%j"
print >> batch, ""
print >> batch, "#SBATCH --mem-per-cpu=1000"
print >> batch, "#SBATCH -t 01:00:00"
print >> batch, "#SBATCH -n 1"
print >> batch, ""
print >> batch, "set rundir=" + root + runDir
print >> batch, "cd ${rundir}"
print >> batch, ""
print >> batch, "set rerun=0"
print >> batch, ""
print >> batch, "set results=${rundir}/results/results$VUORI_JOBINDEX-${rerun}.txt"
print >> batch, "set mask=${rundir}/masks/mask_small_$VUORI_JOBINDEX.jpg"
print >> batch, "set data=${rundir}/../" + imp.getTitle()
print >> batch, ""
print >> batch, "module swap PrgEnv-pgi PrgEnv-gnu/4.7.1"
print >> batch, "setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/v/users/hajaalin/3B/build-gnu/lib"
print >> batch, ""
print >> batch, "/wrk/hajaalin/3B/multispot5_headless  --save_spots ${results} --log_ratios ${mask} ${data}"
print >> batch, ""
batch.close()

# prepare config file
configName = imgDir + runDir + "multispot5.cfg"
config = open(configName, "w")

print >> config, "A=[0.16 0.84 0; 0.495 0.495 0.01; 0 0 1]"
print >> config, "pi=[.5 .5 0]"
print >> config, "add_remove.hessian.inner_samples=1000"
print >> config, "add_remove.hessian.outer_samples=100"
print >> config, "add_remove.optimizer.attempts=10"
print >> config, "add_remove.optimizer.hessian_inner_samples=1000"
print >> config, "add_remove.optimizer.samples=20"
print >> config, "add_remove.thermo.samples=1000"
print >> config, "add_remove.tries=10"
print >> config, "blur.mu=" + str(blur_mu)
print >> config, "blur.sigma=1.00000000000000005551e-01"
print >> config, "cg.max_motion=5.00000000000000000000e-01"
print >> config, "edge=1000"
print >> config, "gibbs.mixing_iterations=1"
print >> config, "intensity.rel_mu=2.00000000000000000000e+00"
print >> config, "intensity.rel_sigma=1.00000000000000000000e+00"
print >> config, "main.cg.max_iterations=5.00000000000000000000e+00"
print >> config, "main.gibbs.samples=10"
print >> config, "main.passes=4"
print >> config, "main.total_iterations=100000000"
print >> config, "max_motion.use_brightness_std=1"
print >> config, 'mode="new"'
print >> config, 'placement="intensity_sampled"'
print >> config, "placement.uniform.num_spots=" + str(initial_spots)
print >> config, "position.extra_radius=2.29999999999999982236e+00"
print >> config, "position.use_prior=1"
print >> config, "preprocess.lpf=5.00000000000000000000e+00"
print >> config, "preprocess.skip=0"
print >> config, "seed=9121164"
print >> config, "//Unmatched tags:"
print >> config, "cluster_to_show=19"
print >> config, "preprocess.fixed_scaling=0"
print >> config, "radius=0"
print >> config, "threshold=0"
print >> config, "use_largest=1"
config.close()
