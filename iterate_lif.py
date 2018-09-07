from ij import IJ,ImagePlus
from loci.plugins.in import ImagePlusReader,ImporterOptions,ImportProcess
import os.path
import sys

def iterateLif(filename,impProcessor):
    """
    Iterate over all series in a LIF file and process them.
    Arguments:
    filename: LIF filename
    impProcessor: processor object, implements method process(ImagePlus).
    """

    opts = ImporterOptions()
    opts.setId(filename)
    opts.setUngroupFiles(True)

    # set up import process
    process = ImportProcess(opts)
    process.execute()
    nseries = process.getSeriesCount()

    # reader belonging to the import process
    reader = process.getReader()

    # reader external to the import process
    impReader = ImagePlusReader(process)
    for i in range(0, nseries):
        print "iterateLif: %d/%d %s" % (i+1, nseries, process.getSeriesLabel(i))

        # activate series (same as checkbox in GUI)
        opts.setSeriesOn(i,True)

        # point import process reader to this series
        reader.setSeries(i)

        # read and process all images in series
        imps = impReader.openImagePlus()
        for imp in imps:
            imp.setTitle("%s_%d_%d" % (imp.getTitle(),i+1,nseries))
            print "iterateLif: " + imp.getTitle()
            try:
                impProcessor.process(imp)
            finally:
                imp.close()

        # deactivate series (otherwise next iteration will have +1 active series)
        opts.setSeriesOn(i, False)
