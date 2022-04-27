import pandas as pd
import numpy as np
import math
from sys import argv

from sqlalchemy import asc

def main(path):
    # Constants
    top = 1
    # Load csv
    csv = pd.read_csv(path)

    # Format header
    header = 'col'
    footer = ''
    for i in range(top):
        header+=',topval'+str(i)+',topimg'+str(i)
        footer+=',botval'+str(i)+',botimg'+str(i)
    header+=footer

    header += ',medval,medimg,meanval,meanimg'

    # Print header
    print(header)

    # Loop through each column
    for col in csv.columns:
        if csv[col].dtype == np.float64:
            s = col.strip()
            # Sort by column
            sorted = csv.sort_values(col, ascending=False)
            
            # Debug
            # print(f'sorted by:{s}')
            # print(sorted[col].tolist())
            
            # Get top N
            s += top_helper(top, col, sorted, 0, lambda x:  x < len(sorted.index), lambda x: x+1)
            # Get bottom N
            s += top_helper(top, col, sorted, len(sorted.index)-1, lambda x: x >= 0, lambda x: x-1)

            # Get Median
            med_i = math.floor(len(sorted.index)/2)
            s += f',{sorted.loc[sorted.index[med_i], col]},{sorted.iloc[med_i, 0]}'
            # Get Mean
            mean = sorted[col].mean()
            mean_name, mean_val = search_bin(col, sorted, mean)
            '''
            Debugging
            mean_name2, mean_val2 = search(col, sorted, mean)
            if mean_val != mean_val2:
                print('BAD RESULT')
                print(f'mean: {mean}, mean1: {mean_val}, mean2: {mean_val2}')
            '''
            s += f',{mean_val},{mean_name} '
            # Print output
            print(s)

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
    return sorted.iloc[closest_i, 0], closest_val

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
    return sorted.iloc[closest[0], 0], sorted.loc[sorted.index[closest[0]], col] # Return name and actual value of the found index   

def top_helper(top, col, sorted, start, check, inc):
    # Set up variables
    s = ''
    found = 0
    index = start

    # Get top n valid values
    while found < top and check(index):
        val = sorted.loc[sorted.index[index], col]
        if (not math.isnan(val)) and val > 0:
            found+=1
            s += f',{val},{sorted.iloc[index, 0]}'
        index = inc(index)
    
    # If there were values missed
    while found < top:
        s+=',null,null'
        found+=1
    
    # Return the built string
    return s

# If called on the command line
if __name__ == '__main__' and len(argv) > 1:
    main(argv[1])