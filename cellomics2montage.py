import glob
from optparse import OptionParser
import os
import re
import sys

reWell = re.compile('(.*_[0-9]{12})_([A-P][0-9]{2})f[0-9]{2}(d[0-9]).tif')
def findPlatesAndWellsAndChannels(inputdir):
    files = glob.glob(inputdir + "/*.tif")
    plates = set()
    wells = set()
    channels = set()
    for f in files:
        d,f = os.path.split(f)
        result = re.match(reWell, f)
        if result:
            plates.add(result.groups()[0])
            wells.add(result.groups()[1])
            channels.add(result.groups()[2])

    return plates, wells, channels

def makeMontage(inputdir, plate, well, channel, tile):
    infiles = inputdir + "/" + plate + "_" + well + "*" + channel + ".tif"
    outputdir = inputdir + "_montage"
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    outfile = outputdir + "/" + plate + "_" + well + channel + ".png"

    cmd = "montage -mode concatenate -tile %s %s %s" % (tile, infiles,outfile)
    print cmd
    os.system(cmd)

if __name__=='__main__':

    parser = OptionParser()
    parser.add_option('-t','--tile', default='5x5')
    options, args = parser.parse_args()

    inputdir = args[0]
    tile = options.tile

    plates,wells,channels = findPlatesAndWellsAndChannels(inputdir)
    for p in plates:
        for w in wells:
            for c in channels:
                makeMontage(inputdir, p, w, c, tile)

