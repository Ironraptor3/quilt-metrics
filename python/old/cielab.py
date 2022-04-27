from colormath.color_objects import LabColor, XYZColor, sRGBColor
from colormath.color_conversions import convert_color
import sys

from importlib_metadata import NullFinder

# The illuminant for adobe prorams (print quality)
illuminant = 'd50'

# Convert a hex string to lab
def hexToLab(hex):
    r,g,b = tuple(int(hex[i:i+2], 16) for i in (0,2,4))
    return rgbToLab(r,g,b)

# Convert rgb format to lab
def rgbToLab(r,g,b):
    rgb = sRGBColor(r,g,b,is_upscaled=True)
    xyz = convert_color(rgb, XYZColor, target_illuminant=illuminant)
    lab = convert_color(xyz, LabColor, target_illuminant=illuminant)
    return lab.lab_l, lab.lab_a, lab.lab_b

# Main function
def main(filename):
    # Open and loop through file
    with open(filename) as file:
        while True:
            line = file.readline()
            if not line:
                break
            line = line.rstrip()
            if len(line) > 0: # Ignore empty lines
                # Split on csv
                vals = line.split(',')
                info = vals[:2]
                palette = vals[2:]
                # For every value in palette, get the corresponding lab and print result
                print(','.join(info + [str(val) for hex in palette for val in hexToLab(hex)]))

if __name__ == '__main__' and len(sys.argv) > 1:
    main(sys.argv[1])
