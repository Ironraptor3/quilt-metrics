import cv2
import numpy as np
from sys import argv
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import matplotlib.pyplot as plt

# Constants
top = 20
max_time = 3

# Main function
# I broke this up into two to prevent an error occuring in the middle
# of this very long operation
def saveDistances(infp, outfp, posCol):
    img = cv2.imread(infp)

    # Set up Grid
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grid = Grid(matrix=np.where(gray>0, 1, 0))

    # Set up PathFinder
    finder = AStarFinder(time_limit=max_time)

    # Set up data
    data = getData(img, posCol)
    
    # Get distances
    dists = np.zeros((len(data), len(data)))
    for i in range(len(data)):
        p1 = data[i]
        # Swapped indicies because it expects (x,y) instead of (r,c)
        start = grid.node(p1[1], p1[0])
        for j in range(i+1, len(data)):
            p2 = data[j]
            end = grid.node(p2[1], p2[0])
            try:
                path, _ = finder.find_path(start, end, grid)
                dists[i,j] = len(path)
                # print(f'{i}-{j}: {len(path)}')
            except Exception as e:
                # Catch timeout and do nothing (default value already in array)
                # print(f'Exception on {i}-{j}: {e}')
                pass
            grid.cleanup()
    
    # In case
    np.save(outfp, dists)

def fromDistances(infp, distsfp, posCol):
    img = cv2.imread(infp)
    data = getData(img, posCol)
    dists = np.load(distsfp)
    
    # Flip over diagonal to fill out
    dists += np.transpose(dists)

    # Subtract 1
    dists -= np.ones(dists.shape)

    # Find the top closest img for each data point
    for i in range(len(data)):
        # Prep indicies
        sorted = dists[i, :].tolist()
        # Save indices
        for j in range(len(sorted)):
            sorted[j] = (j, sorted[j])
        
        # Sort
        sorted.sort(key=lambda x: x[1])

        # Find start
        start = 0
        while sorted[start][1] <= 0 and start < len(sorted):
            start+=1
        end = start+top
        if end > len(sorted):
            end = len(sorted)
        
        data[i] = (data[i][0], data[i][1], sorted[start:end])
    
    # Print data
    printData(img, data)
    # Testing / Feedback
    testResult(img, data, 50)
        

def getData(img, posCol):
    # Find posCol pixels
    result = np.where(np.all(img==posCol,axis=2))
    # Set up data
    data = []
    for r,c in zip(result[0], result[1]):
        data.append((r,c,[]))
    # Return info
    return data

def printData(img, data):
    # For each tuple in the data
    for tup in data:
        # Begin building string (use % position)
        s = f'{tup[0]/img.shape[0]},{tup[1]/img.shape[1]}'
        # For each of its top pairs
        for pair in tup[2]:
            # Append index, distance
            s+=f',{pair[0]},{pair[1]}'
        # Print the build string
        print(s)
    # Done

def testResult(img, data, si):
    color = (0,0,1) # Color for line
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(rgb) # Show the colored image
    startX = data[si][1] # Startpoint X
    startY = data[si][0] # Startpoint Y
    md = max(data[si][2], key=lambda x:x[1])[1] # Maximum distance
    if md <= 0: # Sanity check
        md = 1 # Set default value
    for tup in data[si][2]: # Loop over closest points
        ei = tup[0] # End index
        cs = 1-(tup[1]/md) # Color Scalar
        cf = (color[0]*cs, color[1]*cs, color[2]*cs) # Color final
        endX = data[ei][1] # Endpoint X
        endY = data[ei][0] # Endpoint Y
        # Plot
        plt.plot([startX, endX], [startY, endY], color=cf)
    # Show result
    plt.show()

# Command line
if __name__ == '__main__' and len(argv) > 2:
    # Constant that could be changed to an arg
    posCol = [0,0,255]
    calcDists = True
    if len(argv) > 3:
        calcDists = argv[3] == 'True'
    if calcDists:
        saveDistances(argv[1], argv[2], posCol)
    else:
        fromDistances(argv[1], argv[2], posCol)