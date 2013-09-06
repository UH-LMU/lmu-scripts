import fnmatch
import glob
import logging
import os
import os.path
import re
import shutil
import string
import subprocess
import sys

#from Tkinter import Tk
#from tkFileDialog import askopenfilename


#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
filename = sys.argv[1]

# regexp that defines a Matrix Screener OME Tiff file.
reOME = re.compile('image--L([0-9]+)--S([0-9]+)--U([0-9]+)--V([0-9]+)--J([0-9]+)--E([0-9]+)--O([0-9]+)--X([0-9]+)--Y([0-9]+)--T([0-9]+)--Z([0-9]+)--C([0-9]+).ome.tif')
reStack = re.compile('image--L[0-9]+--S[0-9]+--U[0-9]+--V[0-9]+--J[0-9]+--E[0-9]+--O[0-9]+--X[0-9]+--Y[0-9]+--T[0-9]+')
reExp = re.compile('.*experiment--[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]')

result = reExp.search(filename)
experimentDir = result.group(0)
print "experimentDir:", experimentDir

cellomicsDir = experimentDir + "_cellomics"
if not os.path.isdir(cellomicsDir):
    os.makedirs(cellomicsDir)
else:
    olds = glob.glob(cellomicsDir + "/*.*")
    for old in olds:
        os.remove(old)

row_map = {'00':'A','01':'B', '02':'C', '03':'D', '04':'E', '05':'F', '06':'G', '07':'H' }

col_idx_well = 'U'
row_idx_well = 'V'
col_idx_field = 'X'
row_idx_field = 'Y'

#logging.basicConfig(filename=cellomicsDir+'/matrixscreener2cellomics.log', format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# the regexp that defines the experiment
prog_experiment = re.compile('experiment--[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}')
# the regexp that defines the well
prog_well = re.compile(col_idx_well + '([0-9]+)' + '--' + row_idx_well + '([0-9]+)')
# the regexp that defines the field
prog_field = re.compile(col_idx_field + '([0-9]+)' + '--' + row_idx_field + '([0-9]+)')
# the regexp that defines the channel
prog_c = re.compile('C([0-9]+).ome.tif')

def createPlateCode(base):
    plate_code = re.sub('[^0-9]', '', base, 0)
    plate_code = re.sub('20', '', plate_code, 1)
    plate_code = 'LEICAHCSA-' + plate_code
    return plate_code

def createWellCode(well):
    result_w = prog_well.search(well)
    well_old = result_w.group(0)
    # make column numbers start from 1
    col = int(result_w.group(1) ) + 1
    row = result_w.group(2)
    well_new = row_map[row] + repr(col).zfill(2)
    return well_new

def findFieldIndexRange(fields):
    xmax = 0
    ymax = 0
    for f in fields:
        #print f
        result_f = prog_field.search(f)
        x = result_f.group(1)
        y = result_f.group(2)
        #print x, y
        x = int(x)
        y = int(y)
        xmax = max(x, xmax)
        ymax = max(y, ymax)
    # make indices start from 1, not 0
    return (xmax+1, ymax+1)
    #return (xmax, ymax)

def createFieldCode(xmax, ymax, field):
    result_f = prog_field.search(field)
    x = result_f.group(1)
    y = result_f.group(2)
    x = int(x) + 1
    y = int(y) + 1
    field_new = (y-1)*xmax + x -1
    field_new = repr(field_new).zfill(2)
    return field_new

result = prog_experiment.search(experimentDir)
experiment = result.group(0)
plateCode = createPlateCode(experiment)


# recursively walk the directory and find all tifs,
# store in plate{wells{fields{channels{slices}}}}
plate = {}
for root, dirnames, filenames in os.walk(experimentDir):
  for filename in fnmatch.filter(filenames, '*.tif'):
      result = reOME.search(filename)
#      print filename
      wellId = col_idx_well + result.group(3) + "--" + row_idx_well + result.group(4)
      fieldId = col_idx_field + result.group(8) + "--" + row_idx_field + result.group(9)
      channelId = result.group(12)

      if not plate.has_key(wellId):
          plate[wellId] = {}
      well = plate[wellId]

      if not well.has_key(fieldId):
          well[fieldId] = {}
      field = well[fieldId]

      if not field.has_key(channelId):
          field[channelId] = []
      channel = field[channelId]

      channel.append(root + "/" + filename)



# loop over all wells
for w in plate.keys():
    wellCode = createWellCode(w)
    logging.debug( "Well " + w + " " + wellCode)

    # loop over all fields
    fields = plate[w]
    (xmax, ymax) = findFieldIndexRange(fields)
    for f in fields.keys():
        fieldCode = createFieldCode(xmax, ymax, f)
        logging.debug("Field " + f + " " + fieldCode)        
            
        # convert channels separately
        channels = fields[f]
        for c in channels.keys():
            slices_in = f + '/*C' + c + '.ome.tif'
            
            cellomicsName = cellomicsDir + '/' + plateCode  + '_'+ wellCode + 'f' + fieldCode+ 'd' + str(int(c)) +'.TIF'
            
            # if data is a stack, make projection
            slices = channels[c]
            if len(slices) > 1:
                cmd = ['imgcnv', '-o', cellomicsName,' -project', '-i', slices_in]
                logging.debug(" ".join(cmd))
                os.system(" ".join(cmd))
            else:
                logging.debug("cp " + slices[0] + " " + cellomicsName)
                shutil.copyfile(slices[0], cellomicsName) 


