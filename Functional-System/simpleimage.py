#!/usr/bin/env python3

"""
Stanford CS106A SimpleImage draft, non-final version.
Nick Parlante
 -10/2021 get_pixel() human readable err on bad x,y params
 -4/2020 support RGBA file input
 -11/2019 add in_bounds(x, y) test
 -5/2019 draft version, has file reading, pix, but no foreach

SimpleImage Features:
Create image:
  image = SimpleImage.blank(400, 200)   # create new image of size
  image = SimpleImage('foo.jpg')        # create from file

Access size
  image.width, image.height
  image.in_bounds(x, y) - bool test

Get pix at x,y
  pix = image.get_pix(x, y)
  # pix is RGB tuple like (100, 200, 0)

Set pix at x,y
  image.set_pix(x, y, pix)   # set data by tuple also

Get Pixel object at x,y
  pixel = image.get_pixel(x, y)
  pixel.red = 0
  pixel.blue = 255

Show image on screen
  image.show()

The main() function below demonstrates the above functions as a test.
"""

import sys
# If the following line fails, "Pillow" needs to be installed
from PIL import Image


def clamp(num):
    """
    Return a "clamped" version of the given num,
    converted to be an int limited to the range 0..255 for 1 byte.
    """
    num = int(num)
    if num < 0:
        return 0
    if num >= 256:
        return 255
    return num


class Pixel(object):
    """
    A pixel at an x,y in a SimpleImage.
    Supports set/set .red .green .blue
    and get .x .y
    """
    def __init__(self, image, x, y):
        if type(x) != int or type(y) != int:  # the case where they pass in float
            raise TypeError()  # get_pixel() makes human readable of this
        self.image = image
        self._x = x
        self._y = y

    def __str__(self):
        return 'r:' + str(self.red) + ' g:' + str(self.green) + ' b:' + str(self.blue)

    # Pillow image stores each pixel color as a (red, green, blue) tuple.
    # So the functions below have to unpack/repack the tuple to change anything.

    @property
    def red(self):
        return self.image.px[self._x, self._y][0]

    @red.setter
    def red(self, value):
        rgb = self.image.px[self._x, self._y]
        self.image.px[self._x, self._y] = (clamp(value), rgb[1], rgb[2])

    @property
    def green(self):
        return self.image.px[self._x, self._y][1]

    @green.setter
    def green(self, value):
        rgb = self.image.px[self._x, self._y]
        self.image.px[self._x, self._y] = (rgb[0], clamp(value), rgb[2])

    @property
    def blue(self):
        return self.image.px[self._x, self._y][2]

    @blue.setter
    def blue(self, value):
        rgb = self.image.px[self._x, self._y]
        self.image.px[self._x, self._y] = (rgb[0], rgb[1], clamp(value))

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


# color tuples for background color names 'red' 'white' etc.
BACK_COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
}


class SimpleImage(object):
    def __init__(self, filename, width=0, height=0, back_color=None):
        """
        Create a new image. This case works: SimpleImage('foo.jpg')
        To create a blank image use SimpleImage.blank(500, 300)
        The other parameters here are for internal/experimental use.
        """
        # Create pil_image either from file, or making blank
        if filename:
            self.pil_image = Image.open(filename)
            if (self.pil_image.mode != 'RGB'):
                # Convert to no-alpha format
                no_alpha = Image.new('RGB', self.pil_image.size)
                no_alpha.paste(self.pil_image)
                self.pil_image = no_alpha
            self._filename = filename # hold onto
        else:
            if not back_color:
                back_color = 'white'
            color_tuple = BACK_COLORS[back_color]
            if width == 0 or height == 0:
                raise Exception('Creating blank image requires width/height but got {} {}'
                                .format(width, height))
            self.pil_image = Image.new('RGB', (width, height), color_tuple)
        self.px = self.pil_image.load()
        size = self.pil_image.size
        self._width = size[0]
        self._height = size[1]

    @classmethod
    def blank(cls, width, height, back_color=None):
        """Create a new blank image of the given width and height, optional back_color."""
        return SimpleImage('', width, height, back_color=back_color)

    @classmethod
    def file(cls, filename):
        """Create a new image based on a file, alternative to raw constructor."""
        return SimpleImage(filename)

    @property
    def width(self):
        """Width of image in pixels."""
        return self._width

    @property
    def height(self):
        """Height of image in pixels."""
        return self._height

    def in_bounds(self, x, y):
        """
        Return True if the given x,y is within the width,height bounds of this image
        i.e. get_pixel() a this x,y is valid.
        """
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_pixel(self, x, y):
        """
        Returns a Pixel at the given x,y, suitable for getting/setting
        .red .green .blue values.
        """
        # try/except structure here is all about giving good error messages
        # for various bad x,y params passed in
        try:
            if x < 0 or x >= self._width or y < 0 or y >= self.height:
                e =  Exception('get_pixel bad coordinate x %d y %d (vs. image width %d height %d)' %
                               (x, y, self._width, self.height))
                raise e
            return Pixel(self, x, y)
        except TypeError:
            # coordinate of None or float or string or whatever goes here
            raise Exception('get_pixel coordinates must be int but got x %s y %s' % (x, y))

    def set_rgb(self, x, y, red, green, blue):
        """
        Set the pixel at the given x,y to have
        the given red/green/blue values without
        requiring a separate pixel object.
        """
        self.px[x, y] = (red, green, blue)

    def get_pix(self, x, y):
        """Get pix RGB tuple (200, 100, 50) for the given x,y."""
        return self.px[x, y]

    def set_pix(self, x, y, pix):
        """Set the given pix RGB tuple into the image at the given x,y."""
        self.px[x, y] = pix

    def show(self):
        """Displays the image using an external utility."""
        self.pil_image.show()


def main():
    """
    main() exercises the features as a test.
    1. With 1 arg like flowers.jpg - opens it
    2. With 0 args, creates a yellow square with
    a green stripe at the right edge.
    """
    args = sys.argv[1:]
    if len(args) == 1:
        image = SimpleImage.file(args[0])
        image.show()
        return

    # Create yellow rectangle, using Pixel access.
    image = SimpleImage.blank(400, 200)
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.get_pixel(x, y)
            pixel.red = 255
            pixel.green = 255
            pixel.blue = 0

    # Set green stripe using pix access.
    pix = image.get_pix(0, 0)
    green = (0, pix[1], 0)
    for x in range(image.width - 10, image.width):
        for y in range(image.height):
            image.set_pix(x, y, green)
    image.show()


if __name__ == '__main__':
    main()
