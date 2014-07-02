import glob
import os
import re

class CellomicsUtils:
    def findCreator(self,asnPlate):
        csv = open(asnPlate,'r')
        keys = csv.readline().split(',')
        values = csv.readline().split(',')
        csv.close()
        for i in range(1,len(keys)+1):
            if keys[i] == "Creator":
                return values[i].replace('"','')

    def getTifPath(self,C01,outputDir):
        head,tail = os.path.split(C01)
        tif = os.path.join(outputDir,tail.replace(".C01",".tif"))
        #print "C01:",C01
        #print "TIF:",tif
        return tif
        
    def isDatasetConverted(self,inputDir,outputDir):
        C01s = glob.glob(inputDir + "/*.C01")

        for C01 in C01s:
            tif = self.getTifPath(C01,outputDir)

            # if a tif file is missing, conversion is not complete
            if not os.path.isfile(tif):
                print "C01:",C01
                print "TIF:",tif
                print "TIF file is missing."
                return False
            # if the tif file exists but is older than C01,
            # conversion is not up to date
            else:
                otime = os.stat(C01).st_mtime
                ctime = os.stat(tif).st_mtime
                if otime > ctime:
                    print "C01:",C01
                    print "TIF:",tif
                    print "otime",str(otime)
                    print "ctime",str(ctime)
                    print "TIF file is out of date."
                    return False

        return True

class MatrixUtils:
    rows = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    refirstwell = re.compile('([A-Z])([0-9]+)')
    rematrixwell = re.compile('U([0-9]+)--V([0-9]+)')
    rematrixfield = re.compile('X([0-9]+)--Y([0-9]+)')


    def wellcode(self,matrixname,firstwell='A01'):
        result = re.search(self.rematrixwell,matrixname)
        if result == None:
            raise(Error("Well code not found: " + matrixname))
        u = int(result.group(1))
        v = int(result.group(2))
        
        result = re.search(self.refirstwell,firstwell)
        if result == None:
            raise(Error("Bad well code: " + firstwell))
        offsetu = int(result.group(2))
        offsetv = self.rows.index(result.group(1))

        return self.rows[v+offsetv] + repr(u+offsetu).zfill(2)

    def fieldcode(self,matrixname):
        result = re.search(self.rematrixfield,matrixname)
        if result == None:
            raise(Error("Field code not found: " + matrixname))
        x = int(result.group(1))
        y = int(result.group(2))

        return str(x)+str(y)


class AbcIndex:
    
    def __init__(self):
        self.i = 0
        self.j = 0
        self.k = 0
        self.abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', 'Z']
        
    def next(self):
        next_out = self.abc[self.i] + self.abc[self.j] + self.abc[self.k]
        
        self.k = self.k+1
        if self.k > len(self.abc) -1:
            self.k = 0
            self.j = self.j + 1

        if self.j > len(self.abc) -1:
            self.j = 0
            self.i = self.i + 1
            
        if self.i > len(self.abc) -1:
            return False
            
        return next_out


if __name__=='__main__':

    m = MatrixUtils()
    print m.wellcode('image--L0000--S00--U07--V00--J07--E02--O01--X01--Y00--T0000--Z05--C00.ome.tif')
    print m.wellcode('image--L0000--S00--U07--V00--J07--E02--O01--X01--Y00--T0000--Z05--C00.ome.tif','A01')
    print m.wellcode('image--L0000--S00--U07--V00--J07--E02--O01--X01--Y00--T0000--Z05--C00.ome.tif','B01')
    print m.wellcode('image--L0000--S00--U07--V00--J07--E02--O01--X01--Y00--T0000--Z05--C00.ome.tif','B02')
    print m.wellcode('image--L0000--S00--U00--V00--J07--E02--O01--X01--Y00--T0000--Z05--C00.ome.tif','B02')
    print m.fieldcode('image--L0000--S00--U07--V00--J07--E02--O01--X01--Y00--T0000--Z05--C00.ome.tif')

    c = CellomicsUtils()
    print c.findCreator('/mnt/lmu-active/LMU-active2/users/FROM_CSC_LMU/CellInsight/LMU-CELLINSIGHT_140625100001_converted/metadata/asnPlate.csv')

    dataset = 'LMU-CELLINSIGHT_140625100001'
    dataset = 'LMU-CELLINSIGHT_140210110003'
    base = '/mnt/lmu-active/LMU-active2/users'
    orig = base + '/FROM_CELLINSIGHT/' + dataset
    conv = base + '/FROM_CSC_LMU/CellInsight' + dataset + '_converted'
    c.isDatasetConverted(orig,conv)
    
