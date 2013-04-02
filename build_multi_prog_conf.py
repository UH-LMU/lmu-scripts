#!/usr/bin/env python
from optparse import OptionParser
import os
import string
import subprocess

usage = ''

def main():
    parser = OptionParser(usage=usage)
    parser.add_option('--prog', help="")
    #parser.add_option('--data-dir', help="")
    parser.add_option('--data', help="")
    parser.add_option('--masks-dir', default="masks",  help="")
    parser.add_option('--masks', default="mask", help="")
    parser.add_option('--results-dir', default="results", help="")
    parser.add_option('--results', default="results",  help="")
    parser.add_option('--processors', default=1, help="")
    parser.add_option('--rerun', default=0, help="")

    options, args = parser.parse_args()

    prog = options.prog
    #data_dir = options.data_dir
    data = options.data
    masks_dir = options.masks_dir
    masks = options.masks
    results_dir = options.results_dir
    results = options.results
    processors = int(options.processors)
    rerun = int(options.rerun)
    
    
    
    for i in range(0, processors):
        save_spots = "--save_spots %s/%s%d-%d.txt" % (results_dir,  results,  i, rerun)
        mask = "--log_ratios %s/%s%d.bmp" % (masks_dir,  masks,  i)
        load_checkpoint = ""
        if rerun:
            previous = string.replace(save_spots, '-'+str(rerun),  '-'+str(rerun -1))
            load_checkpoint = "--load_checkpoint " + previous
            
        line = "%d     %s %s %s %s %s" % (i,  prog, load_checkpoint,  save_spots,  mask,  data)

        print line
        
if __name__ == "__main__":
    main()
