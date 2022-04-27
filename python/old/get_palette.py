import os
import sys
from PIL import Image

# How many colors in a quilt-a-day palette
num_colors = 6

# Given a pixel, converts the color to hex
def toHex(pix):
    if len(pix) < 3:
        return "000000"
    return '%02x%02x%02x' % (pix[0], pix[1], pix[2])

# Converts a list of colors to csv format
def palettesToStr(palettes):
    str = ""
    for name, pixels in palettes:
        str+=name
        for pix in pixels:
            str+=','+toHex(pix)
        str+='\n'
    return str

def getAllPalette(dirname): # Obtain csv for folder
    palettes = []
    for filename in os.listdir(dirname):
        if filename.endswith('.png'):
            palette = getPalette(Image.open(dirname + os.sep + filename))
            if len(palette) > 0:
                palettes.append( (filename, palette))
    return palettes

def getPalette(im): # Get the palette for an image
    palette = []
    unsorted = im.getcolors()
    if unsorted == None: # If there was a problem, return an empty list
        return []
    colors = sorted(unsorted, key=lambda t : t[0], reverse=True) # Sort on number of pixels
    for i in range(min(num_colors, len(colors))): # Choose the top colors
        palette.append(colors[i][1])
    return palette


def main(dirname):
    print(palettesToStr(getAllPalette(dirname))) # Simply print to stdout


if __name__ == '__main__' and len(sys.argv) > 1:
    main(sys.argv[1]) # Call main with the first argument provided