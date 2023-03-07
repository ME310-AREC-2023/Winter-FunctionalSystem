#!/usr/bin/env python3

import os
import sys
import math
import numpy

from simpleimage import SimpleImage


def circle(n, r, x0, y0, s, var):
    """
    >>> r = 10
    >>> x0 = 15
    >>> n = 2
    >>> y0 = 20
    >>> s = 4
    >>> var = 0
    >>> circle(n, r, x0, y0, s, var)

    """

    source = range(n)
    delta = (2 * r)/(n - 1)
    xlist_top = list(map((lambda x: round((delta * x)) - r + x0), source))
    xlist_bottom = list(reversed(xlist_top))
    ylist_top = list(map((lambda xl: round(math.sqrt(-(xl-x0)**2 + r**2) + y0) + numpy.random.randint(-s, s)), xlist_top))
    ylist_bottom = list(map((lambda xl: round(-math.sqrt(-(xl - x0)**2 + r**2) + y0) + numpy.random.randint(-s, s)), xlist_bottom))
    xlist = xlist_top + xlist_bottom
    ylist = ylist_top + ylist_bottom
    points = []
    for i in range(2*n):
        points.append(((numpy.random.randint(var, 3*var)), xlist[i], ylist[i]))
    return points


def z_amp(x, y, s, mx, my):
    """
    >>> z_amp(1,1,1,1,1)
    1.0
    """
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
    >>> rgb(0, 255, 125)

    """
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
    # points = [(5, 30, 50), (3, 50, 20), (1, 90, 90), (2, 75, 80)]
    # n = 10
    # r = 20
    # x0 = 50
    # y0 = 50
    # sigma = 3
    # var = 3
    # points1 = circle(n, r, x0, y0, sigma, var)
    # r = 10
    # points2 = circle(n, r, 12, 18, sigma, var)
    # points3 = circle(n, 7, 64, 64, sigma, var)
    # points4 = circle(n, 15, 45, 64, sigma, var)
    # points5 = circle(n, 2, 75, 10, sigma, var)
    # points = points1 + points2 + points3 + points4 + points5
    points = []
    with open("positions.txt") as f:
        for line in f:
            linex_extract = line.split("x=")
            x_p = -int(linex_extract[1][:5])/10
            liney_extract = line.split("y=")
            y_p = int(liney_extract[1][:4])/10
            liney_extract = line.split("q=")
            q = 100*1/int(liney_extract[1][:2])
            points.append((q, x_p, y_p))

    imgs = []
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
                pix = out.get_pixel(x, y)
                new_pix = (pix.red + z_const, pix.green + z_const, pix.blue + z_const)
                out.set_pix(x, y, new_pix)


    for y in range(h):
        for x in range(w):
            pix = out.get_pixel(x, y)
            if (pix.red == 0):
                continue #don't recalculate/reset pixel
            else:
                new_pix = rgb(0, 255, pix.red)
                out.set_pix(x, y, new_pix)
    out.show()

if __name__ == '__main__':
    main()


