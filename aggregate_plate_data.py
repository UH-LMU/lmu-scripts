from itertools import izip
import numpy
import os
from pprint import pprint
import sys
from sqlalchemy import (create_engine, distinct, MetaData, Table, Column, Integer,
    String, DateTime, Float, ForeignKey, and_)
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.ext.automap import automap_base

db = "/mnt/lmu-active/LMU-active1/users/joseph/CellProfiler/output2/resultDB2.db"

# http://stackoverflow.com/questions/14180866/sum-each-value-in-a-list-of-tuples
def sums(rows):
    return map(sum,izip(*rows))

def means(rows):
    return map(numpy.mean,izip(*rows))

class WellPlate:
    ROWS = ['A','B','C','D','E','F','G','H']
    COLS = ['01','02','03','04','05','06','07','08','09','10','11','12']
    cols12 = ',,,,,,,,,,,,\n'

    def __init__(self,name):
        self.name = name
        self.measurements = {}


    def addWellMeasurement(self,well,name,value):
        if not name in self.measurements:
            self.measurements[name] = {}
        self.measurements[name][well] = value


    def addWellMeasurements(self,well,names,values,aggregation):
        if len(names) != len(values):
            print "missing name or value", names, values
            sys.exit(1)

        for i in range(1,len(names)+1):
            self.addWellMeasurement(well,names[i],values[i])

    def _printMeasurement(self,key):
        output = '"%s %s",,,,,,,,,,\n'%(self.name,key)
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
                if well in self.measurements[key]:
                    value = self.measurements[key][well]
                else:
                    value = ""
                values.append(value)
            output = output + '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'% tuple(values)
        return output
    
    def printout(self):
        for m in sorted(self.measurements):
            #pprint(self.measurements[m])
            print self._printMeasurement(m)
            
        

if __name__ == '__main__':
    if not os.path.isfile(db):
        print "db not found"
        sys.exit(1)
        
    engine = create_engine('sqlite:///' + db, echo=False)
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    session = Session(engine)

    # the tables
    image = Base.classes.MyExpt_Per_Image
    nuclei = Base.classes.MyExpt_Per_Object

    # columns for plate and well metadata
    plate = image.Image_Metadata_Plate
    well = image.Image_Metadata_Well

    # data columns of interest
    columnsImage = [#image.ImageNumber,\
                    image.Image_Count_Nuclei,\
                    image.Mean_NucleiExpanded_Intensity_MeanIntensity_Green,\
                    image.StDev_NucleiExpanded_Intensity_MeanIntensity_Green]
    columnsNuclei = [nuclei.NucleiExpanded_Intensity_MeanIntensity_Green,\
                    #nuclei.NucleiExpanded_Intensity_MedianIntensity_Green,\
                    nuclei.NucleiExpanded_Intensity_IntegratedIntensity_Green]

    # find unique plate names
    plates = session.query(distinct(plate)).all()
    #print plates
    
    for p in plates:
        p = p[0]
        #print "Plate %s, looking for wells..." % p[0]
        
        # find wells
        wells = session.query(distinct(well)).filter(plate==p).all()
        #print p[0],wells

        wellplate= WellPlate(p)
        for w in wells:
            w = w[0]

            # get image level measurements
            queryImages = session.query(*columnsImage).filter(plate==p,well==w) \
                          .filter(image.Image_Count_Nuclei > 0)

            results = queryImages.all()
            s = sums(results)
            m = means(results)
            #print w, s, m
            wellplate.addWellMeasurement(w, str(columnsImage[0]) + " (well sum of field nuclei counts)",s[0])
            wellplate.addWellMeasurement(w, str(columnsImage[1]) + " (well average of field averages)",m[1])
            wellplate.addWellMeasurement(w, str(columnsImage[2]) + " (well average of field stdevs)",m[2])


            # get measurements for all nuclei 
            queryNuclei = session.query(*columnsNuclei).join(image,nuclei.ImageNumber==image.ImageNumber) \
                          .filter(plate==p,well==w)

            results = queryNuclei.all()
            s = sums(results)
            m = means(results)
            #print w, s, m
            wellplate.addWellMeasurement(w, str(columnsNuclei[0]) + " (average of all cells in well)",m[0])
            wellplate.addWellMeasurement(w, str(columnsNuclei[1]) + " (sum of all cells in well)",s[1])
            wellplate.addWellMeasurement(w, "Count_of_All_Nuclei_Per_Well",len(results))

##            # test average
##            queryAvg = session.query(func.avg(columnsNuclei[0].label('average')))\
##                       .join(image,nuclei.ImageNumber==image.ImageNumber) \
##                       .filter(plate==p,well==w) \
##                       .all()
##            
##            wellplate.addWellMeasurement(w, str(columnsNuclei[0]) + " (average of all cells in well TEST)",str(queryAvg[0]))


            # get measurements for nuclei that are not too bright  
            # http://stackoverflow.com/questions/2002024/how-to-use-mathematic-equations-as-filters-in-sqlalchemy
            # clause = "intensity < mean + std"
            clause = nuclei.NucleiExpanded_Intensity_MeanIntensity_Green < \
                     image.Mean_NucleiExpanded_Intensity_MeanIntensity_Green + \
                     image.StDev_NucleiExpanded_Intensity_StdIntensity_Green
            queryNuclei = queryNuclei.filter(clause)
            
            results = queryNuclei.all()
            s = sums(results)
            m = means(results)
            #print w, s, m
            wellplate.addWellMeasurement(w, str(columnsNuclei[0]) + " (average of not too bright cells in well)",m[0])
            wellplate.addWellMeasurement(w, str(columnsNuclei[1]) + " (sum of not too bright cells in well)",s[1])
            wellplate.addWellMeasurement(w, "Count_of_Not_Too_Bright_Nuclei_Per_Well",len(results))

        wellplate.printout()
        #sys.exit()
                                          
        

