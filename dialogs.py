import os
import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *

class ConverterDialog(Tkinter.Frame):

    def __init__(self, root, converter=None):

        self.converter = converter

        Tkinter.Frame.__init__(self, root)

        # options for buttons
        button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

        self.DEFAULT_OUTPUTROOT = "OUTPUT ROOT DIRECTORY NOT SET"
        self.vin = StringVar()
        self.vin.set("INPUT DIRECTORY NOT SET")
        self.voutroot = StringVar()
        self.voutroot.set(self.DEFAULT_OUTPUTROOT)
        self.vout = StringVar()
        self.vout.set("OUTPUT DIRECTORY NOT SET")
        self.voutleaf = StringVar()
        self.vmask = StringVar()
        self.vmask.set('*')

        # define buttons
        Tkinter.Button(self, text='Select input directory', command=self.askinputdirectory).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vin).pack(**button_opt)
        Tkinter.Label(self, text='File filter (e.g. *J07*)').pack(**button_opt)
        Tkinter.Entry(self, textvariable=self.vmask).pack(**button_opt)
        Tkinter.Button(self, text='Select output root directory', command=self.askoutputdirectory).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.voutroot).pack(**button_opt)
        Tkinter.Label(self, textvariable=self.vout).pack(**button_opt)

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'Select directory'

    def askinputdirectory(self):

        """Returns a selected directoryname."""

        dirname = tkFileDialog.askdirectory(**self.dir_opt)
        head,tail = os.path.split(dirname)
        self.vin.set(dirname)

        if self.voutroot.get() == self.DEFAULT_OUTPUTROOT:
            self.voutroot.set(head)

        self.voutleaf.set(tail+ "_stacks")
        self.vout.set(self.voutroot.get() + "/" + self.voutleaf.get())

    def askoutputdirectory(self):

        """Returns a selected directoryname."""

        dirname = tkFileDialog.askdirectory(**self.dir_opt)
        self.voutroot.set(dirname)
        self.vout.set(self.voutroot.get() + "/" + self.voutleaf.get())

    def startconversion(self):
        print "Convertingconverting..."
        print self.vin.get()
        print self.vout.get()

        if self.converter != None:
            self.converter.convert(self.vin.get(),self.vout.get())

        
class Matrix2StacksDialog(ConverterDialog):
    def __init__(self,root,converter=None):
        ConverterDialog.__init__(self,root,converter)
        
        self.vabc = IntVar()
        #Tkinter.Checkbutton(self, text="Add ABC", variable=self.vabc).pack()
        self.vwellcodes = IntVar()
        #Tkinter.Label(self, text="Prepend well and field codes").pack()
        Tkinter.Checkbutton(self, text="Prepend well and field codes",variable=self.vwellcodes).pack()
        
        self.vfirstwell = StringVar()
        self.vfirstwell.set("A01")
        Tkinter.Label(self, text="First well").pack()
        Tkinter.Entry(self, textvariable=self.vfirstwell).pack()
        
        Tkinter.Button(self, text="Start conversion", command=self.startconversion).pack()

    def startconversion(self):
        print "Matrix2StacksDialog converting..."
        print self.vin.get()
        print self.vout.get()
        print self.vabc.get()
        print self.vmask.get()
        print self.vfirstwell.get()
        
        if self.converter != None:
            self.converter.convert(self.vin.get(),self.vout.get(),self.vwellcodes.get(),self.vfirstwell.get(),self.vmask.get())
           
if __name__=='__main__':
    root = Tkinter.Tk()
    #ConverterDialog(root).pack()
    Matrix2StacksDialog(root).pack()
    root.mainloop()
