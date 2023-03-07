#!/usr/bin/env python3

import os
import sys
import math

from simpleimage import SimpleImage


def z_amp(x, y, s, mx, my):
    """
    >>> z_amp(1,1,1,1,1)
    1.0
    """
    mag = 255/(s**2)
    z = round(mag*math.exp(-((mx - x)**2 + (my - y)**2)/(2*s**2)))
    return z


def main():
    args = sys.argv[1:]
    w = 100
    h = 100
    out = SimpleImage.blank(w, h, 'black')
    points = [(5, 30, 50), (3, 50, 20), (1, 90, 90), (2, 75, 80)]
    imgs = []
    for point in points:
        s = point[0]
        mx = point[1]
        my = point[2]
        img = SimpleImage.blank(w, h, 'black')
        for y in range(h):
            for x in range(w):
                z_const = z_amp(x, y, s, mx, my)
                z = (z_const, z_const, z_const)
                img.set_pix(x, y, z)
        imgs.append(img)

    for img in imgs:
        for y in range(h):
            for x in range(w):
                pix = out.get_pixel(x, y)
                pix_add = img.get_pixel(x, y)
                new_pix = (pix.red + pix_add.red, pix.green + pix_add.green, pix.blue + pix_add.blue)
                out.set_pix(x, y, new_pix)
    out.show()

if __name__ == '__main__':
    main()


