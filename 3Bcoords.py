import os.path
import sys

filename = sys.argv[1]
file = open(filename, 'r')
lines = file.readlines()
file.close()

box = sys.argv[2]
(x0,y0,width,height) = box.split(',')
x0 = float(x0)
y0 = float(y0)
width = float(width)
height = float(height)
print x0,y0,width,height

(root,ext) = os.path.splitext(filename)
filename = root + "_trimmed" + ext
print filename
file = open(filename, 'w')

for l in lines:
    (x,y,z) = l.split()
    x = float(x)
    y = float(y)
    z = float(z)

    if x0 < x and x < (x0+width) and y0 < y and y < (y0+height):
        print >> file, x, y, z

file.close()

