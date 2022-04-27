import cv2
import math
import numpy as np
from sys import argv

# Constants
size = 3

# Main function
def main(file, outfile, pcol):
    # Read
    img = cv2.imread(file)

    # Grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calculate downscaled dimensions
    rows = math.ceil(img_gray.shape[0] / size)
    cols = math.ceil(img_gray.shape[1] / size)

    # Padding
    img = np.zeros((img_gray.shape[0] + (img_gray.shape[0] % size),
        img_gray.shape[1] + (img_gray.shape[1] % size)))
    
    img[:img_gray.shape[0], :img_gray.shape[1]] = img_gray

    # Init grid
    grid = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            grid[i,j] = pcol if pcol in img[i*size:(i+1)*size, j*size:(j+1)*size] else 0

    # Save grid
    cv2.imwrite(outfile, grid)

# Command line
if __name__ == '__main__' and len(argv) > 2:
    pcol = 255
    if len(argv) > 3:
        pcol = int(argv[3])
    main(argv[1], argv[2], pcol)