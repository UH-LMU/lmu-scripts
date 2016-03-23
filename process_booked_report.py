#!/bin/env python
import codecs
import copy
import csv
from datetime import datetime, timedelta, time
from optparse import OptionParser
import os
import re
import sys
from time import mktime, strptime
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *

# these must correspond with elomake field names
AFFILIATION_ACADEMIC = "Academic"
AFFILIATION_PRIVATE = "Private company"

# these must correspond with booked-lmu/lmu/constants.php
RESC_WORKSTATION_3D="3D Workstation"
RESC_WORKSTATION_2D="2D Workstation"
RESC_WORKSTATION_HCA="HCA Workstation"
RESC_3I_MARIANAS="3I Marianas"
RESC_ZEISS_LSM_700="Zeiss LSM 700"
RESC_LEICA_SP5="Leica TCS SP5"
RESC_LEICA_SP5_MP="Leica TCS SP5 MP SMD FLIM"
RESC_LEICA_SP5_HCS="Leica SP5 II HCS A"
RESC_CELL_IQ="Cell-IQ"
RESC_CELL_IQ_FLUOR="Cell-IQ Fluorescence"
RESC_CELLINSIGHT="CellInsight"
RESC_LEICA_DM6000="Leica DM6000"

# these are defined here to deal with special prices
RESC_3I_MARIANAS_WITHOUT_LASERS="3I Marianas without lasers"
RESC_3I_MARIANAS_WITH_LASERS="3I Marianas with lasers"

# these must correspond with Booked report headers / attribute names
H_ACCOUNT = "Account"
H_USER = "User"
H_PI = "PI"
H_REMIT_AREA_CODE = "Remit area code"
H_WBS = "WBS"
H_RESOURCE = u'\ufeff"Resource"'
H_RESOURCE = "Resource"
H_BEGIN = "Begin"
H_END = "End"
H_TITLE = "Title"
H_DESCRIPTION = "Description"
H_AFFILIATION = "Affiliation type"
H_LASERS_NONE = "Laser-None"
H_OVERTIME = "Overtime"
H_RESERVATION_ID = "Reference Number"

# these headers are defined for adding pricing data
H_SECTION_BEGIN = "Section begin"
H_SECTION_END = "Section end"
H_DURATION = "Duration"
H_PRICE_CATEGORY = "Price category"
H_PRICE_PER_HOUR = "Price per hour"
H_PRICE_TOTAL = "Total price"

TIME_PRIME="prime time"
TIME_NIGHT="night time"
TIME_OTHER="other time"

PRICE_LIST = {}
# http://www.biocenter.helsinki.fi/bi/lmu/prices_acad.htm
PRICE_LIST[AFFILIATION_ACADEMIC] = {\
RESC_LEICA_SP5:{TIME_PRIME:22,TIME_OTHER:17,TIME_NIGHT:12.5},\
RESC_LEICA_SP5_MP:{TIME_PRIME:22,TIME_OTHER:17,TIME_NIGHT:12.5},\
RESC_LEICA_SP5_HCS:{TIME_PRIME:22,TIME_OTHER:17,TIME_NIGHT:12.5},\
RESC_ZEISS_LSM_700:{TIME_PRIME:18,TIME_OTHER:14,TIME_NIGHT:10},\
RESC_3I_MARIANAS_WITH_LASERS:{TIME_PRIME:18,TIME_OTHER:14,TIME_NIGHT:10},\
RESC_3I_MARIANAS_WITHOUT_LASERS:{TIME_PRIME:9,TIME_OTHER:6,TIME_NIGHT:4.5},\
RESC_LEICA_DM6000:{TIME_PRIME:3,TIME_OTHER:1,TIME_NIGHT:1},\
RESC_CELLINSIGHT:{TIME_PRIME:9,TIME_OTHER:6,TIME_NIGHT:5},\
RESC_CELL_IQ:{TIME_PRIME:2,TIME_OTHER:2,TIME_NIGHT:2},\
RESC_CELL_IQ_FLUOR:{TIME_PRIME:2,TIME_OTHER:2,TIME_NIGHT:2},\
RESC_WORKSTATION_3D:{TIME_PRIME:5,TIME_OTHER:3,TIME_NIGHT:3},\
RESC_WORKSTATION_HCA:{TIME_PRIME:5,TIME_OTHER:3,TIME_NIGHT:3},\
RESC_WORKSTATION_2D:{TIME_PRIME:3,TIME_OTHER:1,TIME_NIGHT:1},\
}
# http://www.biocenter.helsinki.fi/bi/lmu/prices_comm.htm
PRICE_LIST[AFFILIATION_PRIVATE] = {\
RESC_LEICA_SP5:{TIME_PRIME:132,TIME_OTHER:102,TIME_NIGHT:75},\
RESC_LEICA_SP5_MP:{TIME_PRIME:132,TIME_OTHER:102,TIME_NIGHT:75},\
RESC_LEICA_SP5_HCS:{TIME_PRIME:132,TIME_OTHER:102,TIME_NIGHT:75},\
RESC_ZEISS_LSM_700:{TIME_PRIME:108,TIME_OTHER:84,TIME_NIGHT:60},\
RESC_3I_MARIANAS_WITH_LASERS:{TIME_PRIME:108,TIME_OTHER:84,TIME_NIGHT:60},\
RESC_3I_MARIANAS_WITHOUT_LASERS:{TIME_PRIME:54,TIME_OTHER:36,TIME_NIGHT:27},\
RESC_LEICA_DM6000:{TIME_PRIME:18,TIME_OTHER:6,TIME_NIGHT:6},\
RESC_CELLINSIGHT:{TIME_PRIME:54,TIME_OTHER:36,TIME_NIGHT:30},\
RESC_CELL_IQ:{TIME_PRIME:12,TIME_OTHER:12,TIME_NIGHT:12},\
RESC_CELL_IQ_FLUOR:{TIME_PRIME:12,TIME_OTHER:12,TIME_NIGHT:12},\
RESC_WORKSTATION_3D:{TIME_PRIME:30,TIME_OTHER:18,TIME_NIGHT:18},\
RESC_WORKSTATION_HCA:{TIME_PRIME:30,TIME_OTHER:18,TIME_NIGHT:18},\
RESC_WORKSTATION_2D:{TIME_PRIME:18,TIME_OTHER:6,TIME_NIGHT:6},\
}

OUTPUT_COLUMNS = [H_ACCOUNT,H_REMIT_AREA_CODE,H_WBS,\
H_USER, H_TITLE,H_DESCRIPTION,H_RESOURCE,H_LASERS_NONE,H_BEGIN,H_END,\
H_SECTION_BEGIN,H_SECTION_END,H_DURATION,H_PRICE_CATEGORY,H_AFFILIATION,H_PRICE_PER_HOUR,H_OVERTIME,H_PRICE_TOTAL]

def get_datetime( instr ):
    try:
        return datetime.fromtimestamp(mktime(strptime(instr, '%d/%m/%Y %H:%M:%S')))
    except:
        return datetime.fromtimestamp(mktime(strptime(instr, '%d/%m/%Y %H:%M')))

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

class BookedReportProcessorDialog(Tkinter.Frame):

    def __init__(self, root, converter=None):

        self.converter = converter

        Tkinter.Frame.__init__(self, root)

        # options for buttons
        button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        self.vin1 = StringVar()
        self.vin1.set("INPUT FILE NOT SET")
        self.vin2 = StringVar()
        self.vin2.set("")
        self.vin3 = StringVar()
        self.vin3.set("PI")

        # define buttons
        Tkinter.Button(self, text='Select report file', command=self.askinputfile1).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vin1).pack(**button_opt)
        Tkinter.Button(self, text='Select billing info file', command=self.askinputfile2).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vin2).pack(**button_opt)
        Tkinter.Label(self, text="Group key in billing info").pack()
        Tkinter.Entry(self, textvariable=self.vin3).pack()

        Tkinter.Button(self, text="Split report", command=self.startconversion).pack()

        # defining options for opening a directory
        self.file_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['parent'] = root
        options['title'] = 'Select file'
        options['filetypes'] = [('csv files', '.csv')]

    def askinputfile1(self):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        self.vin1.set(filename)

    def askinputfile2(self):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        self.vin2.set(filename)

    def startconversion(self):
        print self.vin1.get()
        print self.vin2.get()
        print self.vin3.get()

        csvFile = self.vin1.get()
        billingInfo = None
        if self.vin2.get() != "":
            billingInfo = BillingInfo(self.vin2.get(), self.vin3.get())

        processor = BookedReportProcessor(csvFile)
        processor.process(billingInfo)

        # if self.converter != None:
        #     self.converter.convert(self.vin.get(),self.vout.get(),self.vwellcodes.get(),self.vfirstwell.get(),self.vmask.get())

class BookedReportProcessor:

    def __init__(self, csvFile):
        self.csvFile = csvFile
        head,tail = os.path.splitext(csvFile)
        self.csvFileOut = head + "_split" + tail
        #print self.csvFileOut

        # remove BOM
        # http://stackoverflow.com/questions/8898294/convert-utf-8-with-bom-to-utf-8-with-no-bom-in-python
        BUFSIZE = 4096
        BOMLEN = len(codecs.BOM_UTF8)

        path = csvFile
        with open(path, "r+b") as fp:
            chunk = fp.read(BUFSIZE)
            if chunk.startswith(codecs.BOM_UTF8):
                i = 0
                chunk = chunk[BOMLEN:]
                while chunk:
                    fp.seek(i)
                    fp.write(chunk)
                    i += len(chunk)
                    fp.seek(BOMLEN, os.SEEK_CUR)
                    chunk = fp.read(BUFSIZE)
                fp.seek(-BOMLEN, os.SEEK_CUR)
                fp.truncate()

        headers = None
        self.content = {}

        #print('Reading file %s' % csvFile)
        #reader=csv.reader(open(csvFile))
        reader=unicode_csv_reader(open(csvFile))
        firstRow = True
        for row in reader:
            # skip empty rows
            if len(row) == 0:
                continue

            if firstRow:
                """
                If we are on the first line, create the headers list from the first row.
                """
                headers = row
                headers[0]=headers[0].replace("u'\ufeff'","")
                #print headers

                # find index of begin, account, reservation_id
                i_account = headers.index(H_ACCOUNT)
                i_begin = headers.index(H_BEGIN)
                i_reservation_id = headers.index(H_RESERVATION_ID)
                firstRow = False
                self.headers = headers
            else:
                """
                Create keys we can use for sorting.
                """
                account = row[i_account]
                begin = str(get_datetime(row[i_begin]))
                reservation_id = row[i_reservation_id]
                key = "%s_%s_%s" % (account,begin,reservation_id)
                #print key.encode('utf-8')
                self.content[key] = dict(zip(headers, row))


    def print_header(self):
        out = u''
        for c in OUTPUT_COLUMNS:
            out = '%s,"%s"' % (out,c)

        return out# + "\n"

    def print_reservation(self,r):
        out = u''
        for c in OUTPUT_COLUMNS:
            out = '%s,"%s"' % (out,r[c])

        return out# + "\n"

    def split_reservation(self,row, billingInfo):
        # remove newlines from description
        row[H_DESCRIPTION] = row[H_DESCRIPTION].replace("\r\n","; ")

        resource = row[H_RESOURCE]
        start = row[H_BEGIN]
        end = row[H_END]
        affiliation = row[H_AFFILIATION]
        overtime = row[H_OVERTIME]

        # academic use by default
        if affiliation == "":
            affiliation = AFFILIATION_ACADEMIC
        #print resource, start, end, affiliation, overtime

        # update billing info if given
        if billingInfo != None:
            # PI email used in Booked
            pi = row[H_PI]
            # account name used in OCF
            account = row[H_ACCOUNT]

            # try first PI email
            rec = billingInfo.getRemitAreaCode(pi)
            # try next account name
            if rec == None:
                rec = billingInfo.getRemitAreaCode(account)
            if rec != None:
                row[H_REMIT_AREA_CODE] = rec

            wbs = billingInfo.getWBS(pi)
            if wbs == None:
                wbs = billingInfo.getWBS(account)
            if wbs != None:
                row[H_WBS] = wbs

        # check if 3I Marianas is booked with lasers
        if resource == RESC_3I_MARIANAS:
            if row[H_LASERS_NONE] == "1":
                resource = RESC_3I_MARIANAS_WITHOUT_LASERS
            else:
                resource = RESC_3I_MARIANAS_WITH_LASERS

        start = get_datetime(start)
        end = get_datetime(end)

        # first define timepoints where prices can change
        split_points = []
        split_date = start.date()
        while split_date <= end.date():
            split_points.append( datetime.combine(split_date, time(8,0)))
            split_points.append( datetime.combine(split_date, time(9,0)))
            split_points.append( datetime.combine(split_date, time(17,0)))
            split_points.append( datetime.combine(split_date, time(22,0)))

            split_date = split_date + timedelta(days=1)
        #print split_points

        split_start = start
        for i in range(0,len(split_points) - 1):
            t1 = max(split_points[i],start)
            t2 = min(split_points[i+1],end)

            if t2 <= t1: continue

            section = copy.deepcopy(row)
            section[H_SECTION_BEGIN] = t1
            section[H_SECTION_END] = t2

            if t1.time() == time(22,0) and t2.time() == time(8,0):
                section[H_PRICE_CATEGORY] = TIME_NIGHT
                #print t1, t2, TIME_NIGHT

            elif (t1.time() >= time(9,0) and t2.time() <= time(17,0)):
                section[H_PRICE_CATEGORY] = TIME_PRIME
                #print t1, t2, TIME_PRIME

            else:
                section[H_PRICE_CATEGORY] = TIME_OTHER
                #print t1, t2, TIME_OTHER

            price_per_hour = PRICE_LIST[affiliation][resource][section[H_PRICE_CATEGORY]]
            section[H_PRICE_PER_HOUR] = price_per_hour
            #print price_per_hour

            duration = t2 - t1
            section[H_DURATION] = duration
            #print duration

            overtime = 1
            if section[H_OVERTIME] == 1:
                price_per_hour = price_per_hour * 2
                overtime = 2

            price_total = float(duration.seconds) / (60*60) * price_per_hour * overtime
            section[H_PRICE_TOTAL] = price_total
            #print price_total

            return self.print_reservation(section).encode('utf-8')

    def process(self, billingInfo):
        output = open(self.csvFileOut, 'w')
        print >> output, self.print_header().encode('utf-8')
        sorted_keys = sorted(self.content.keys())
        for k in sorted_keys:
            print >> output, self.split_reservation(self.content[k], billingInfo)
        output.close()

# Helper class for reading billing info from another file
class BillingInfo:

    WBSs = {}
    remitAreaCodes = {}

    def __init__(self, csvFile, keyColumn):
        reader=unicode_csv_reader(open(csvFile))

        firstRow = True
        for row in reader:
            # skip empty rows
            if len(row) == 0:
                continue

            if firstRow:
                """
                If we are on the first line, create the headers list from the first row.
                """
                headers = row
                headers[0]=headers[0].replace("u'\ufeff'","")
                #print headers

                # find index of begin, account, reservation_id
                i_key = headers.index(keyColumn)
                i_rec = headers.index(H_REMIT_AREA_CODE)
                i_wbs = headers.index(H_WBS)
                firstRow = False
            else:
                #print row[i_key].encode('utf-8'), row[i_rec].encode('utf-8'), row[i_wbs].encode('utf-8')
                self.remitAreaCodes[row[i_key].encode('utf-8')] = row[i_rec].encode('utf-8')
                self.WBSs[row[i_key].encode('utf-8')] = re.sub("[^0-9]", "", row[i_wbs].encode('utf-8'))

        #print self.remitAreaCodes

    def getRemitAreaCode(self, email):
        if self.remitAreaCodes.has_key(email):
            return self.remitAreaCodes[email]
        else:
            return None

    def getWBS(self, email):
        if self.WBSs.has_key(email):
            return self.WBSs[email]
        else:
            return None


if __name__=='__main__':

    usage ="""%prog [options] input_directory

    Split Booked report to prime, night and other time slots.
    Run '%prog -h' for options.
    """

    parser = OptionParser(usage=usage)
    parser.add_option('-i', '--input', help="Input report.")
    parser.add_option('-b', '--billing', help="Billing info.")
    parser.add_option('-k', '--key', help="Billing info group key.")
    options, args = parser.parse_args()

    # use command line arguments, if they were given
    if options.input:
        csvFile = options.input
        billingInfo = None
        if options.billing:
            billingInfo = BillingInfo(options.billing, options.key)

        processor = BookedReportProcessor(csvFile)
        processor.process(billingInfo)
    else:
        root = Tkinter.Tk()
        BookedReportProcessorDialog(root).pack()
        root.mainloop()
