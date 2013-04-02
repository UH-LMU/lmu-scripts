#!/usr/bin/env python
from math import sqrt
from math import floor
from math import ceil
from optparse import OptionParser
import os
import subprocess

usage = ''

def main():
    parser = OptionParser(usage=usage)
    parser.add_option('-W', '--data-width', help="")
    parser.add_option('-H', '--data-height', help="")
    parser.add_option('-N', '--processors', help="")
    parser.add_option('-x', '--x0', help="")
    parser.add_option('-y', '--y0', help="")
    parser.add_option('-u', '--roi-width', help="")
    parser.add_option('-v', '--roi-height', help="")
    parser.add_option('-o', '--overlap', default="3",  help='')

    options, args = parser.parse_args()
    
    dataX = int(options.data_width)
    dataY = int(options.data_height)
    N = int(options.processors)
    x0 = int(options.x0)
    y0 = int(options.y0)
    roiX = int(options.roi_width)
    roiY = int(options.roi_height)
    overlap = int(options.overlap)
    format = 'gif'

    nx = range(1,  N+1)
    print nx
    
    ny = []
    for n in nx:
        #ny.append(int(round(N/n)))
        ny.append(round(N/n))
        
    print ny
    
    minratio = 9999999990
    imin = 0
    for i in range(0, len(nx)):
        dx = roiX / nx[i]
        dy = roiY / ny[i]
        #print i,  roiX,  roiY,  nx[i],  ny[i],  dx,  dy
        ratio = 1 - min(dx, dy)/max(dx, dy)
        print i,  nx[i],  ny[i],  dx,  dy,  ratio,  minratio
        if ratio < minratio and nx[i]*ny[i] == N:
            minratio = ratio
            imin = i
    
    print imin
    nx = nx[imin]
    ny = ny[imin]
    print nx,  ny,  nx*ny
    dx = int(floor(roiX / nx))
    dy = int(floor(roiY / ny))
    print dx,  dy
    print dx*nx,  dy*ny
        
    filename = 'convert_3b.sh'
    file = open(filename,  'w')
    
    composite_small = 'mask_small_sum.' + format
    composite_large = 'mask_large_sum.' + format
    cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:white', composite_small]
    print >> file, ' '.join(cmd)
    cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:white', composite_large]
    print >> file, ' '.join(cmd)
    
    for i in range(0, nx):
        for j in range(0, ny):
            startx = x0 + i*dx
            starty = y0 + j*dy
            endx = startx + dx
            endy = starty + dy
            print i,  j,  startx,  endx,  starty,  endy

            startx_L = x0 + i*dx - overlap
            starty_L = y0 + j*dy - overlap
            endx_L = startx + dx + overlap
            endy_L = starty + dy + overlap
            print i,  j,  startx_L,  endx_L,  starty_L,  endy_L
            
            index = str(i*int(ny)+j)
            maskname_small = 'mask_small'+ index
            mask_small = maskname_small +'.'+ format 
            maskname_large = 'mask_large'+index
            mask_large = maskname_large +'.'+ format 
            cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:black', '-stroke','skyblue', '-fill','skyblue', '-draw','\"rectangle '+str(startx)+','+str(starty)+ ' '+str(endx)+','+str(endy)+'\"',  mask_small ]
            print >> file, ' '.join(cmd) 
            cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:black', '-stroke','skyblue', '-fill','skyblue', '-draw','\"rectangle '+str(startx_L)+','+str(starty_L)+ ' '+str(endx_L)+','+str(endy_L)+'\"',  mask_large ]
            print >> file, ' '.join(cmd) 
            cmd = ['composite', composite_small, '-compose',  'minus',  mask_small,   composite_small]
            print >> file, ' '.join(cmd)
            cmd = ['composite', composite_large, '-compose',  'minus',  mask_large,   composite_large]
            print >> file, ' '.join(cmd)
            
            cmd = ['convert', '-threshold',  '0.5',  mask_small,   maskname_small + '.bmp']
            print >> file, ' '.join(cmd)
            cmd = ['convert', '-threshold',  '0.5',  mask_large,   maskname_large + '.bmp']
            print >> file, ' '.join(cmd)
            
            print >> file, 'rm ' + mask_small    
            print >> file, 'rm ' + mask_large    
        
    file.close()
    os.system('chmod a+rx ' + filename)
    #subprocess.call(filename)    
    
if __name__ == "__main__":
    main()
