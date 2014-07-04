from itertools import izip
import numpy
import os
import sys
from sqlalchemy import (create_engine, distinct, MetaData, Table, Column, Integer,
    String, DateTime, Float, ForeignKey, and_)
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

db = "/mnt/lmu-active/LMU-active1/users/joseph/CellProfiler/output/DefaultDB.db"

def sums(rows):
    return map(sum,izip(*rows))

def means(rows):
    return map(numpy.mean,izip(*rows))

class WellPlate96:
    ROWS = ['A','B','C','D','E','F','G','H']
    COLS = ['01','02','03','04','05','06','07','08','09','10','11','12']
    cols12 = ',,,,,,,,,,,\n'

    def __init__(self,name,headers,data):
        self.name = name
        self.headers = headers
        #self.data = data
        self.sums = {}
        self.means = {}
        for well in data.keys():
            self.sums[well] = sums(data[well])
            self.means[well] = means(data[well])

    def printout(self):
##        output = '"%s",,,,,,,,,,,\n'%self.name
##        output = output + cols12
##        
        for h in self.headers:
            print str(h)
        print self.sums['A01']

        

if __name__ == '__main__':
    if not os.path.isfile(db):
        print "db not found"
        sys.exit(1)
        
    engine = create_engine('sqlite:///' + db, echo=False)
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    session = Session(engine)

    # the table
    image = Base.classes.MyExpt_Per_Image

    # columns for plate and well metadata
    plate = image.Image_Metadata_Plate
    well = image.Image_Metadata_Well

    # data columns of interest
    dataheaders = [image.ImageNumber,\
                   image.Image_Count_Nuclei,\
                   image.Image_Intensity_MeanIntensity_Green]
    
    # find unique plate/well combinations
    plates_and_wells = session.query(plate,well).group_by(plate,well).all()
    plates = session.query(distinct(plate)).all()
    
    #for pw in plates_and_wells:
        #results = session.query(*data).filter(plate==pw[0],well==pw[1]).all()
    for p in plates:
        print p
        wells = session.query(distinct(well)).filter(plate==p[0]).all()
        print p,wells

        data = {}
        for w in wells:
            #print p,w
            results = session.query(*dataheaders).filter(plate==p[0],well==w[0]).all()
            #print p,w,results
            data[w[0]] = results

        plate = WellPlate96(p[0],dataheaders,data)
        plate.printout()
        sys.exit()
                                          
        

