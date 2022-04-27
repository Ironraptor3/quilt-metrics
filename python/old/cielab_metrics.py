import sys
import math
import numpy as np

# Alias for distance between two lab colors
def dist(lab1, lab2):
    return math.dist(lab1,lab2)

# Distance between two colors with taxicab distance used for luminance (more accurate on colors further apart)
def dist_taxi(lab1, lab2):
    return math.dist(lab1[1:], lab2[1:]) + dist_lum(lab1, lab2)

# Distance between luminance values in lab colors
def dist_lum(lab1, lab2):
    return abs(lab1[0]-lab2[0])

# List of metrics to use
metrics = [dist, dist_taxi, dist_lum]

# Calculate all metrics
def getMetrics(labs):
    result = []
    for f in metrics:
        v = []
        # All combinations
        for i in range(len(labs)):
            for j in range(i+1, len(labs)):
                v.append(f(labs[i], labs[j])) # Call f(lab1, lab2)
        result.append(v)
    return result # Return the result

# Main function
def main(filename):
    # Open and loop through file
    with open(filename) as file:
        print(','.join(['folder','name'] + [title + f.__name__ for title in ['mean ', 'variance '] for f in metrics]))
        while True:
            line = file.readline()
            if not line:
                break
            line = line.rstrip()
            if len(line) > 0: # Skip empty lines
                vals = line.split(',') # Split on csv values
                info = vals[:2]
                labs = vals[2:]
                size = 3
                # Get all labs (they are 3-tuples of (l*a*b*))
                labs = [ np.array(labs[pos:pos+size]).astype(np.float64) for pos in range(0, len(labs), size)]
                # Call get metrics
                result = getMetrics(labs)
                # Print info alongside mean and variance of each metric using numpy
                print(','.join(info+np.mean(result, axis=1).astype(str).tolist()+np.var(result, axis=1).astype(str).tolist()))

if __name__ == '__main__' and len(sys.argv) > 1:
    main(sys.argv[1])