import numpy as np
from sklearn.mixture import GaussianMixture as GM
import sys

# Gets the Gaussian Mixture Model
def getGM(filename, n_components, columns):
    with open(filename) as file:
        header = file.readline().rstrip().split(',')
        # Find indices of each requested field
        indices = [header.index(col) for col in columns]
        
        arr = []
        while True:
            line = file.readline()
            if not line:
                break
            line = line.rstrip()
            if len(line) > 0:
                line = line.split(',')
                # Append all desired fields
                arr.append([float(line[index]) for index in indices])
        # Fit the Gaussian Mixture Model to the array
        return GM(n_components=n_components).fit(np.array(arr))

# Main function
def main(filename, n_components, columns):
    # Print the Gaussian Mixture Model
    print(getGM(filename, n_components, columns).means_)

if __name__ == '__main__' and len(sys.argv) > 3:
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3:])