#!/usr/bin/env python3

import os
import sys
import math
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import readPosText  # local lib
import pullPos_InfluxDB as getPositions
import pushLocPop_InfluxDB as pushLocPop

from simpleimage import SimpleImage
from PIL import Image

# image constants
image_xy_zero = (67.0, 0.)
w = 1674
h = 1371
magScalar = 0.1 # normal dist mangitude scalar

# global var
filename = 'images/test' #def save area
saveProgress = False # default to not saving in-progress pictures


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
    mag = magScalar * 255/(s**2)
    z = round(mag*math.exp(-((mx - x)**2 + (my - y)**2)/(2*(30*s)**2)))
    return z

def z_radius(s):
    """
    Define the maxim radius for which `z_amp` is non-zero
    """
    if (s > 5.3):
        # print(f'R limilted, s = {s}')
        return int(225)
    else:
        # print(f's = {s}')
        mag = magScalar * 255/(s**2)
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
    mx = int(df['position_x']*100 + image_xy_zero[0])
    my = int(df['position_y']*100 + image_xy_zero[1])
    my = h - my # reverse direction
    # mx = w - mx # reverse reverse!
    if (mx < 370 and my < 300):
        return #skip if not "worn"
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

def remapColorScheme(mat):
    out = SimpleImage.blank(w, h, 'black') # create locally
    for y in range(h):
        for x in range(w):
            pix = mat[x,y]
            if (abs(pix) < 0.01):
                continue #don't recalculate/reset pixel
            else:
                new_pix = rgb(0, 255, pix)
                out.set_pix(x, y, new_pix)
    return out

def overlayOnBackground(mat, color):
    c = 0.5
    cutoff = 40
    # color = Image.open("Color.jpg")
    # out = Image.open("Gray.jpg")
    back = Image.open("images/RoomLayoutTables.jpg")
    for y in range(h):
        for x in range(w):
            threshold = mat[x,y] # from B&W image
            if threshold < 1:
                continue #no change, don't do math here
            rbase, gbase, bbase = back.getpixel((x, y))
            # threshold, g, b = out.getpixel((x, y))
            colorPix = color.get_pixel(x, y)
            if threshold < cutoff:
                c = 0.5 * (threshold/cutoff)**1.5
            red = int((rbase + c * colorPix.red) / (1 + c))
            green = int((gbase + c * colorPix.green) / (1 + c))
            blue = int((bbase + c * colorPix.blue) / (1 + c))
            back.putpixel((x, y), (red, green, blue))
    # back.show()
    return back # return new image

def LocationPopularity(mat):
    totalSum = np.sum(mat.sum()) #total summation
    # print(totalSum)
    if (totalSum < 1):
        #something very bad happened, skip!
        print('Utilization is too low!')
        return

    locales = {'AREC':((0,328), (460, 930)), 'Volvo':((0,938),(460, 1390)),\
               'Avatar':((902, 910), (1364, 1432)), 'JnJ':((902, 380), (1364, 900))}
    sums = {}
    percentages = {} # blank for now
    remaining = 100.0 #how much is unaccounted for?
    for key in locales:
        indices = locales[key] # extrac tuples
        sums[key] = np.sum(mat[indices[0][0]:indices[1][0], indices[0][1]:indices[1][1]])
        percentages[key] = [sums[key]/totalSum * 100]
        remaining -= percentages[key][0] # how much is left?
        # print(f'{key}: {sums[key]}, {percentages[key]}%')
    percentages['Travelling'] = [remaining]
    df = pd.DataFrame(percentages).T
    # print(df)

    # send to InfluxDB
    # pushLocPop.writeLocationPop(percentages)
    plot = df.plot.bar(legend=False, rot=0, \
                       title=f"Location Popularity in ME310 at {time.strftime('%H:%M')}",\
                       ylabel='% Time Spent with each Team')
    fig = plot.get_figure()
    return fig
    # fig.savefig(filename+ '_LocPop.png')

def main(args):
    filename = args[0] # where to save?
    if (len(args) > 0):
        saveProgress = True #enable us to save other images
        timestr = time.strftime("%y%m%d-%H%M%S")
    print(filename + '/bckgnd/' + timestr + '.jpg')

    points_df = pd.DataFrame()

    # open the file, read in the positions
    # points_df = readPosText.read_DTRLS_logfile("positions.txt")
    iDB_client = getPositions.init_client()
    points_df = getPositions.pullData(iDB_client)

    mat = np.zeros((w,h))
    out = SimpleImage.blank(w,h, 'black') # create an empty image
    
    points_df.apply(lambda x: plotPoints(x, mat), axis = 1)


    out = remapColorScheme(mat)
    if saveProgress:
        out.save(filename + '/bckgnd/' + timestr + '.jpg')

    # Location Popularity
    fig = LocationPopularity(mat)
    if (fig is not None):
        fig.savefig(filename+ '/LocPop/' + timestr + '.jpg')

    #overlay with background image
    overlay = overlayOnBackground(mat, out)
    overlay.save(filename + '/overlay/' + timestr + '.jpg')

if __name__ == '__main__':
    main(sys.argv[1:])


