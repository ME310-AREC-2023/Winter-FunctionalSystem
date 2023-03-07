#!/usr/bin/env python3

import os
import sys
import math
import numpy
import readPosText # local lib

from simpleimage import SimpleImage



def z_amp(x, y, s, mx, my):
    """
    Calculate a "heat" based on location.

    x,y is current location (calcs distance to base point)
    mx, my is base point, center of the hotspot
    s - standard deviation? implies how wide the spread is
    """
    # """
    # >>> z_amp(1,1,1,1,1)
    # 1.0
    # """
    mag = 0.3 * 255/(s**2)
    z = round(mag*math.exp(-((mx - x)**2 + (my - y)**2)/(2*(30*s)**2)))
    return z

def z_radius(s):
    """
    Define the maxim radius for which `z_amp` is non-zero
    """
    mag = 0.3 * 255/(s**2)
    radius = math.sqrt((2*(30*s)**2) * math.log(mag))
    return int(round(radius *1.25)) # include a fudge factor

def rgb(minimum, maximum, value):
    """
    Rescale value for heat map coloring
    """
    # """
    # >>> rgb(0, 255, 125)

    # """
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(.9 - ratio)))
    r = int(max(0, 255*(ratio - .9)))
    g = 255 - b - r
    t = 20
    b = int(b/1.5)
    if value < t:
        r = int(r * value/t)
        g = int(g * value/t)
        b = int(b * value/t)
    return r, g, b

def main():
    args = sys.argv[1:]
    w = 1000
    h = 1000
    out = SimpleImage.blank(w, h, 'black')
    points = []

    # open the file, read in the positions
    points = readPosText.read_DTRLS_logfile("positions.txt")

    out = SimpleImage.blank(w,h, 'black') # create an empty image

    for point in points:
        s = int(point[0])
        mx = int(point[1])
        my = int(point[2])
        radius = z_radius(s) #how far do we need to search?

        for y in range(my - radius, my + radius):
            for x in range(mx - radius, mx + radius):
                # calculate new value to add
                z_const = z_amp(x, y, s, mx, my)

                # add to existing B&W heatmap
                out.increment_rgb(x, y, z_const, z_const, z_const)


    for y in range(h):
        for x in range(w):
            pix = out.get_pixel(x, y)
            if (pix.red == 0):
                continue #don't recalculate/reset pixel
            else:
                new_pix = rgb(0, 255, pix.red)
                out.set_pix(x, y, new_pix)
    # out.show() # programaticallly save it instead
    out.save('images/MaxTest.jpg')

if __name__ == '__main__':
    main()


