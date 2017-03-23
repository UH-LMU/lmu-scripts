from iterate_lif import iterateLif
from ij import IJ,ImagePlus
import os.path
import sys

class LifExporter:
    """
    <imagej> export_lif.py <lif> <exportDirectory>
    Fiji.app/ImageJ-linux64 export_lif.py experiment.lif export
    """

    def __init__(self,exportDir):
        self.exportDir = exportDir

    def process(self,imp):
        IJ.saveAsTiff(imp, os.path.join(self.exportDir,imp.getTitle()))
        for c in range(1,imp.getNChannels()+1):
            imp.setPosition(c,1,1)
            impc = ImagePlus(imp.getTitle() + "_c" + str(c), imp.getProcessor())
            print impc.getTitle()
            IJ.saveAsTiff(impc, os.path.join(self.exportDir,impc.getTitle()))
            impc.close()

def main():
    filename = sys.argv[1]
    exportDir = sys.argv[2]

    exporter = LifExporter(exportDir)

    iterateLif(filename,exporter)

if __name__ == "__main__":
    main()
