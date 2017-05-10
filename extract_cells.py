from iterate_lif import iterateLif
from ij import IJ,ImagePlus,ImageStack
from ij.gui import Roi, WaitForUserDialog as Wait
from ij.measure import Measurements, ResultsTable
from ij.plugin.filter import ParticleAnalyzer
from optparse import OptionParser
import os
import os.path
import sys

class CellExtractor:
    """
    <imagej> extract_cells.py <lif> <outputdir>
    extract_cells.py experiment.lif output
    """

    def __init__(self,nucleusChannel, minArea, maxArea, boxSize, edge, nCells, debug, slices, exportDir):
        self.nucleusChannel = nucleusChannel
        self.exportDir = exportDir
        self.minArea = minArea
        self.maxArea = maxArea
        self.boxSize = boxSize
        self.edge = boxSize
        self.nCells = nCells
        self.debug = debug
        self.slices = slices

    def process(self,imp):
        # extract nucleus channel, 8-bit and twice binned
        imp.setC(self.nucleusChannel)
        ip = imp.getChannelProcessor().duplicate()
        ip = ip.convertToByteProcessor()
        ip = ip.bin(4)
        nucleus = ImagePlus("nucleus_channel", ip)

        # threshold image and separate clumped nuclei
        IJ.run(nucleus, "Auto Threshold", "method=Otsu white setthreshold show");
        IJ.run(nucleus, "Make Binary", "thresholded remaining black");
        IJ.run(nucleus, "Watershed", "");

        directory = imp.getTitle()
        directory = directory.replace(" ", "_")\
            .replace(",", "_")\
            .replace("#", "_series")\
            .replace("...", "")\
            .replace(".","_")
        directory = os.path.join(self.exportDir, directory)
        sliceDirectory = os.path.join(directory, "slices")
        print directory
        print sliceDirectory
        if not os.path.exists(sliceDirectory):
            os.makedirs(sliceDirectory)

        # Create a table to store the results
        table = ResultsTable()

        # Create a hidden ROI manager, to store a ROI for each blob or cell
        #roim = RoiManager(True)

        # remove small particles and border particles
        pa = ParticleAnalyzer(\
            ParticleAnalyzer.ADD_TO_MANAGER | ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES,\
            Measurements.CENTER_OF_MASS,\
            table,\
            self.minArea, self.maxArea,\
            0.0,1.0)

        if pa.analyze(nucleus):
            print "All ok, number of particles: ", table.size()
        else:
            print "There was a problem in analyzing", imp, nucleus
        table.save(os.path.join(directory, "rt.csv"))

        # read the center of mass coordinates
        cmx = table.getColumn(0)
        cmy = table.getColumn(1)

        if self.debug:
            imp.show()

        i=0
        for i in range(0, min(self.nCells,table.size())):
            # ROI around the cell
            cmx = table.getValue("XM",i)
            cmy = table.getValue("YM",i)
            x = 4 * cmx - (self.boxSize - 1) / 2
            y = 4 * cmy - (self.boxSize - 1) / 2
            if (x < self.edge or y < self.edge or x > imp.getWidth() - self.edge or y > imp.getHeight() - self.edge):
                continue
            roi = Roi(x,y,self.boxSize,self.boxSize)
            imp.setRoi(roi, False)

            cellStack = ImageStack(self.boxSize, self.boxSize)

            for z in range(1, imp.getNSlices() + 1):
                imp.setSlice(z)
                for c in range(1, imp.getNChannels() + 1):
                    imp.setC(c)
                    # copy ROI to stack
                    imp.copy()
                    impSlice = imp.getClipboard()
                    cellStack.addSlice(impSlice.getProcessor())
                    if self.slices:
                        sliceTitle = "cell_%s_z%s_c%s" % (str(i).zfill(4), str(z).zfill(3), str(c))
                        print sliceTitle
                        IJ.saveAsTiff(impSlice, os.path.join(sliceDirectory, sliceTitle))
                    impSlice.close()

            title = "cell_" + str(i).zfill(4)
            cell = ImagePlus(title, cellStack)

            # save ROI image
            IJ.saveAsTiff(cell, os.path.join(directory, title))
            cell.close()

            if self.debug:
                imp.updateAndDraw()
                wait = Wait("particle done")
                wait.show()


def main():

    usage = "usage: <imagej> %prog [options] lif outputdir\n" + \
            "example: Fiji.app/ImageJ-linux64 extract_cells.py -i 50 -a 400 -b 301 -c 3 /data/images /data/output"
    parser = OptionParser(usage=usage)
    parser.add_option('-i','--min_area',\
            default='40',\
            help='Minimum area for nuclei (default=%default).')
    parser.add_option('-a','--max_area',\
            default='600',\
            help='Maximum area for nuclei (default=%default).')
    parser.add_option('-b','--box_size',\
            default='251',\
            help='Box size for cells (odd, default=%default).')
    parser.add_option('-c','--channel',\
            default='1',\
            help='Nucleus channel (default=%default).')
    parser.add_option('-e','--edge',\
            default='100',\
            help='Nucleus channel (default=%default).')
    parser.add_option('-n','--ncells',\
            default='100',\
            help='Number of cells (default=%default).')
    parser.add_option('-d','--debug',\
            action="store_true", \
            default=False, \
            help='Debug mode, show intermediate steps (default=%default).')
    parser.add_option('-s','--slices',\
            action="store_true", \
            default=False, \
            help='Save individual slices and channels (default=%default).')
    (opts,args) = parser.parse_args()

    print opts
    print args

    filename = sys.argv[1]
    output = sys.argv[2]

    extractor = CellExtractor(int(opts.channel), int(opts.min_area), int(opts.max_area),\
                            int(opts.box_size), int(opts.edge), int(opts.ncells), opts.debug, opts.slices, output)

    iterateLif(filename,extractor)

if __name__ == "__main__":
    main()
