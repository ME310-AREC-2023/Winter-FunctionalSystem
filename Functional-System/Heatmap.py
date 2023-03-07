#!/usr/bin/env python3

import os
import sys
import math
import numpy as np
import pandas as pd
import readPosText  # local lib
import pullPos_InfluxDB as getPositions

from simpleimage import SimpleImage

# image constants
image_xy_zero = (670, 0)
w = 1676
h = 1373


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
    if (s > 5.3):
        print(f'R limilted, s = {s}')
        return int(225)
    else:
        print(f's = {s}')
        mag = 0.3 * 255/(s**2)
        # print(s, mag)
        radius = math.sqrt(np.abs((2*(30*s)**2) * math.log(mag)))
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

def plotPoints(df, mat):
    s = 100/df['position_quality'] # extra transform
    mx = int(df['position_x'] + image_xy_zero[0])
    my = int(df['position_y'] + image_xy_zero[1])
    radius = z_radius(s) #how far do we need to search?

    for y in range(my - radius, my + radius):
        for x in range(mx - radius, mx + radius):
            if (x < 0 or x >= w or y < 0 or y >= h):
                continue #don't break if we are outside bounds
            # calculate new value to add
            z_const = z_amp(x, y, s, mx, my)

            # add to existing B&W heatmap
            # out.increment_rgb(x, y, z_const, z_const, z_const)
            mat[x,y] += z_const

def main():
    args = sys.argv[1:]
    out = SimpleImage.blank(w, h, 'black')
    points_df = pd.DataFrame()

    # open the file, read in the positions
    # points_df = readPosText.read_DTRLS_logfile("positions.txt")
    iDB_client = getPositions.init_client()
    points_df = getPositions.pullData(iDB_client)

    mat = np.zeros((w,h))
    out = SimpleImage.blank(w,h, 'black') # create an empty image
    
    points_df.apply(lambda x: plotPoints(x, mat), axis = 1)


    for y in range(h):
        for x in range(w):
            # pix = out.get_pixel(x, y)
            pix = mat[x,y]
            if (abs(pix) < 0.01):
                continue #don't recalculate/reset pixel
            else:
                new_pix = rgb(0, 255, pix)
                out.set_pix(x, y, new_pix)
    # out.show() # programaticallly save it instead
    out.save('images/DWM_Test1.jpg')

if __name__ == '__main__':
    main()


