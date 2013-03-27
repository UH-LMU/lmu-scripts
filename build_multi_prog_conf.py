#!/usr/bin/env python
from optparse import OptionParser
import os
import subprocess

usage = ''

def main():
    parser = OptionParser(usage=usage)
    parser.add_option('--prog', help="")
    parser.add_option('--data-dir', help="")
    parser.add_option('--data', help="")
    parser.add_option('--masks-dir', default="masks",  help="")
    parser.add_option('--masks', default="mask", help="")
    parser.add_option('--results-dir', default="results", help="")
    parser.add_option('--results', default="results",  help="")
    parser.add_option('--processors', help="")

    options, args = parser.parse_args()

    prog = options.prog
    data_dir = options.data_dir
    data = options.data
    masks_dir = options.masks_dir
    masks = options.masks
    results_dir = options.results_dir
    results = options.results
    processors = int(options.processors)
    
    for i in range(0, processors):
        line = "%d     %s --save_spots %s/%s%d.txt --log_ratios %s/%s%d.bmp %s" % (i,  prog, results_dir,  results,  i, masks_dir,  masks,  i,  data )
        print line
        
if __name__ == "__main__":
    main()
