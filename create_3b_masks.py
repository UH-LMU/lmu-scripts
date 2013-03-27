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

    nx = range(1,  round(sqrt(N))+1)
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
        if ratio < minratio:
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
    
    # add three pixels for overlapping boundaries
    rectx = dx + overlap
    recty = dy + overlap
    
    filename = 'convert_3b.sh'
    file = open(filename,  'w')
    
    #'-colorspace','Gray',
    composite = 'mask_sum.' + format
    cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:white', composite]
    print >> file, ' '.join(cmd)
    border = 'border.' + format
    cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:black', '-stroke','skyblue', '-fill','skyblue', \
                '-draw','\"rectangle '+str(x0)+','+str(y0)+ ' '+str(x0 + overlap)+','+str(y0 + roiY)+'\"',   \
                '-draw','\"rectangle '+str(x0)+','+str(y0)+ ' '+str(x0 + roiX)+','+str(y0 + overlap)+'\"',   \
                '-draw','\"rectangle '+str(x0+roiX-overlap)+','+str(y0)+ ' '+str(x0+roiX)+','+str(y0 + roiY)+'\"',   \
                '-draw','\"rectangle '+str(x0)+','+str(y0+roiY-overlap)+ ' '+str(x0 + roiX)+','+str(y0 + roiY)+'\"',  border ]
    print >> file, ' '.join(cmd)
    cmd = ['composite', composite, '-compose',  'minus',  border,   composite]
    print >> file, ' '.join(cmd)
    
    composite_roi = 'mask_sum_roi.' + format
    cmd = ['convert', '-size', str(roiX)+'x'+str(roiY), 'xc:white', composite_roi]
    print >> file, ' '.join(cmd)
    border_roi = 'border_roi.' + format
    cmd = ['convert', '-size', str(roiX)+'x'+str(roiY), 'xc:black', '-stroke','skyblue', '-fill','skyblue', \
                '-draw','\"rectangle '+str(0)+','+str(0)+ ' '+str(overlap)+','+str(roiY)+'\"',   \
                '-draw','\"rectangle '+str(0)+','+str(0)+ ' '+str(roiX)+','+str(overlap)+'\"',   \
                '-draw','\"rectangle '+str(roiX-overlap)+','+str(0)+ ' '+str(roiX)+','+str(roiY)+'\"',   \
                '-draw','\"rectangle '+str(0)+','+str(roiY-overlap)+ ' '+str(roiX)+','+str(roiY)+'\"',  border_roi ]
    print >> file, ' '.join(cmd)
    cmd = ['composite', composite_roi, '-compose',  'minus',  border_roi,   composite_roi]
    print >> file, ' '.join(cmd)
    
    for i in range(0, nx):
        for j in range(0, ny):
            startx = x0 + i*dx
            starty = y0 + j*dy
            endx = x0 + i*dx + rectx
            endy = y0 + j*dy + recty
            
            maskname = 'mask'+str(i*(nx-1)+j)
            mask = maskname +'.'+ format 
            cmd = ['convert', '-size', str(dataX)+'x'+str(dataY), 'xc:black', '-stroke','skyblue', '-fill','skyblue', '-draw','\"rectangle '+str(startx)+','+str(starty)+ ' '+str(endx)+','+str(endy)+'\"',  mask ]
            print >> file, ' '.join(cmd) 
            cmd = ['composite', composite, '-compose',  'minus',  mask,   composite]
            print >> file, ' '.join(cmd)
            cmd = ['convert', '-threshold',  '0.5',  mask,   maskname + '.bmp']
            print >> file, ' '.join(cmd)
            
            print >> file, 'rm ' + mask    
    
            startx = 0 + i*dx
            starty = 0 + j*dy
            endx = 0 + i*dx + rectx
            endy = 0 + j*dy + recty

            mask_roi = 'mask_roi'+str(i*nx+j)+'.'+ format 
            cmd = ['convert', '-size', str(roiX)+'x'+str(roiY), 'xc:black', '-stroke','skyblue', '-fill','skyblue', '-draw','\"rectangle '+str(startx)+','+str(starty)+ ' '+str(endx)+','+str(endy)+'\"',  mask_roi ]
            print >> file, ' '.join(cmd) 
            cmd = ['composite', composite_roi, '-compose',  'minus',  mask_roi,   composite_roi]
            print >> file, ' '.join(cmd)
    
    file.close()
    os.system('chmod a+rx ' + filename)
    #subprocess.call(filename)    
    
if __name__ == "__main__":
    main()
