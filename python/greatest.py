import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype
from PIL import Image
from sys import argv
import math
import pandas as pd
import numpy as np

# main function
def main(path, output):
    # Load csv
    df = pd.read_csv(path)
    # Get columns
    cols = [col for col in df if is_numeric_dtype(df[col])]
    # Make subplots
    fig, plots = plt.subplots(len(cols), 4)
    # Get figure size
    ipi = 3 # Inches per picture
    fig.set_size_inches(ipi*4, ipi*len(cols))
    # Loop through each column
    for i in range(len(cols)):
        col = cols[i]
        sorted = df.sort_values(col)
        # Highest
        highest_i = len(sorted.index)-1
        write_example(plots, sorted, col, highest_i, i, 0, "Highest: ")
        # Lowest
        lowest_i = 0
        write_example(plots, sorted, col, lowest_i, i, 1, "Lowest: ")
        # Get Median
        med_i = math.floor(len(sorted.index)/2)
        write_example(plots, sorted, col, med_i, i, 2, "Median: ")
        # Get Mean
        mean = sorted[col].mean()
        mean_i = search_bin(col, sorted, mean)
        write_example(plots, sorted, col, mean_i, i, 3, "Mean: ")
    fig.tight_layout() # Make tight layout
    # Save layout
    if output is not None:
        plt.savefig(output, dpi=200)
    # Display layout
    else:
        plt.show()

# Writes an image to the subplots
def write_example(plots, sorted, col, index, pr, pc, prefix):
    # Get the image name
    img_name = sorted.iloc[index, 0]
    # DEBUG print(img_name)
    # Open the image
    with Image.open(img_name) as img:
        img_val = sorted.loc[sorted.index[index], col]
        # Show the image
        plots[pr, pc].imshow(img)
        # Could be shortened
        # Adjusts title
        plots[pr, pc].set(title=col+'_'+prefix+str(img_val))

# Searches for the value in ascending order
# Deprecated
def search(col, sorted, mean):
    closest_i = 0 # Start at 0
    closest_val = None # Start undefined
    for i in range(len(sorted.index)): # Look in ascending order
        val = sorted.loc[sorted.index[i], col] # Value at location
        if val >= mean: # Stop when value is >= (we are at or passed the value being searched for)
            if closest_val is not None and mean-closest_val < val-mean: # Check the previous value to see if it was closer
                closest_val = val # Update closest_value
                closest_i = i # Also update this var
        else: # Continue updating the variables
            closest_val = val
            closest_i = i
    # Return result
    return closest_i

# Efficient and better (semantically, looking at results) search
def search_bin(col, sorted, mean):
    bound = len(sorted.index) # Top bound is the length of the matrix
    top = bound # Start at top bound
    bot = 0 # Start at 0
    index = 0 # Arbitrary assignment
    while top != bot: # If top == bot, then we are done
        index = (top-bot)//2 # Get index of midpoint
        val = sorted.loc[sorted.index[index], col] # Get value at this location
        if val > mean: # Searching in a region with too high values
            top = index # Bring the top bound down
        elif val < mean: # Searching in a region with too low values
            bot = index # Bring the bot bound up
        else: # Found the exact value!
            break
        # Additional check to stop the loop in the case of a degenerate matrix size to start
        if index == top or index == bot:
            break
    # Init neighbors
    neighbors = []
    if index > 0: # if not at edge
        neighbors.append(index-1) # Append 1 lower index
    neighbors.append(index) # Append the index settled on
    if index < bound-1: # if not at other edge
        neighbors.append(index+1) # Append 1 higher index
    neighbors = [(n, np.abs(mean-sorted.loc[sorted.index[n], col])) for n in neighbors] # Find differences and save as tuples
    closest = min(neighbors, key=lambda x: x[1]) # Find the minimum distance from the mean value
    return closest[0] # Return index of best match 

# If called on the command line
if __name__ == '__main__' and len(argv) > 1:
    # Initialize output
    output = None
    # Read 2nd argument
    if len(argv) > 2:
        output = argv[2]
    # Call main
    main(argv[1], output)