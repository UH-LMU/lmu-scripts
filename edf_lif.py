from iterate_lif import iterateLif
from edf_process_headless import edfProcess
from ij import IJ,ImagePlus
from ij.io import DirectoryChooser,OpenDialog
from edfgui import Parameters
import os.path
import sys

class EdfWorker:
    """
    <imagej> edf_lif.py <lif> <exportDirectory>
    Fiji.app/ImageJ-linux64 export_lif.py experiment.lif export
    """

    def __init__(self,exportDir, params):
        self.exportDir = exportDir
        self.params = params

    def process(self,imp):
        # skip automerged images
        if "Merging" in imp.getTitle():
            return
        
        title = imp.getTitle() + "_edf"
        print "EdfWorker.process: " + title
        output = edfProcess(imp, self.params)
        IJ.saveAsTiff(output, os.path.join(self.exportDir,title))

def main():
    #filename = sys.argv[1]
    #exportDir = sys.argv[2]

    inputDir = "/mnt/med-groups-lmu/ls1/users/l/lsalomie/"
    defaultName = "lif.lif"
    outputDir = "/home/hajaalin/tmp/lifexporttest"

    filename = OpenDialog("Choose LIF",inputDir,defaultName).getPath()
    if not filename:
        # user canceled dialog
        return
    
    chooser = DirectoryChooser("Choose export directory")
    chooser.setDefaultDirectory(outputDir)
    exportDir = chooser.getDirectory()
    if not exportDir:
        # user canceled dialog
        return

    # EDF parameters
    params = Parameters()
    params.setQualitySettings(params.QUALITY_HIGH)
    params.nScales = 10

    worker = EdfWorker(exportDir,params)

    iterateLif(filename,worker)

if __name__ in ("__builtin__", "__main__"):
    main()
