from itertools import izip
import numpy
import os
import sys
from sqlalchemy import (create_engine, distinct, MetaData, Table, Column, Integer,
    String, DateTime, Float, ForeignKey, and_)
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

db = "/mnt/lmu-active/LMU-active1/users/joseph/CellProfiler/output/DefaultDB.db"

# http://stackoverflow.com/questions/14180866/sum-each-value-in-a-list-of-tuples
def sums(rows):
    return map(sum,izip(*rows))

def means(rows):
    return map(numpy.mean,izip(*rows))


class WellPlate96:
    ROWS = ['A','B','C','D','E','F','G','H']
    COLS = ['01','02','03','04','05','06','07','08','09','10','11','12']
    cols12 = ',,,,,,,,,,,,\n'

    def __init__(self,name,headers,data):
        self.name = name
        self.headers = headers
        #self.data = data
        self.sums = {}
        self.means = {}
        for well in data.keys():
            self.sums[well] = sums(data[well])
            self.means[well] = means(data[well])

    def _add_aggregate(self,output,aggregate,label,i):
        output = output + '"%s %s %s",,,,,,,,,,\n'%(self.name,label,self.headers[i])
        # add column labels
        output = output + ','
        for c in self.COLS:
            output = output + '"%s",'%c
        output = output + '\n'

        for r in self.ROWS:
            output = output + '"%s",' % r
            values = []
            for c in self.COLS:
                well = r+c
                if aggregate.has_key(well):
                    value = aggregate[well][i]
                else:
                    value = ""
                values.append(value)
            output = output + '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'% tuple(values)
        return output
    

    def printout(self):
        output = ''
        #output = '"%s",,,,,,,,,,,\n'%self.name
        #output = output + self.cols12
        
        for h in self.headers:
            i = self.headers.index(h)
            output = self._add_aggregate(output,self.sums,"SUM",i)
            output = output + self.cols12
            output = self._add_aggregate(output,self.means,"MEAN",i)
            output = output + self.cols12

        print output

        

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
    plates = session.query(distinct(plate)).all()
    #print plates
    
    for p in plates:
        #print "Plate %s, looking for wells..." % p[0]
        wells = session.query(distinct(well)).filter(plate==p[0]).all()
        #print p[0],wells

        data = {}
        for w in wells:
            #print p,w
            results = session.query(*dataheaders).filter(plate==p[0],well==w[0]).all()
            #print p,w,results
            data[w[0]] = results
        #print data

        wellplate = WellPlate96(p[0],dataheaders,data)
        wellplate.printout()
        #sys.exit()
                                          
        

