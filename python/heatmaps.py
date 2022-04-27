from sys import argv
from pandas.api.types import is_numeric_dtype
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# A function which normalizes a column
def norm_col(col):
    # Only normalize numeric columns
    if is_numeric_dtype(col):
        # Get the maximum and minimum
        max = col.max()
        min = col.min()
        # Subtract minimum
        col = col-min
        # Get range
        diff = max-min
        if diff != 0:
            # Divide by range if nonzero
            col = col / diff
    # Return result
    return col

# Main function
def main(path, norm_output, hist_output):
    # Read dataframe
    df = pd.read_csv(path)
    # Normalize the dataframe
    df = df.apply(norm_col)
    # Get valid columns
    cols = [col for col in df if is_numeric_dtype(df[col])]
    # How many combinations are there?
    combos = len(cols) * ((len(cols) - 1) / 2)
    # Make a square grid to accomodate the combinations
    sq = int(np.ceil(np.sqrt(combos)))
    # Generate subplots from matplotlib
    fig, plots = plt.subplots(sq, sq, sharex=True, sharey=True)
    # fig.suptitle('Heatmaps')
    ipg = 3 # Inches per graph
    # Update figure size
    fig.set_size_inches(ipg*sq, ipg*sq)
    prow = 0
    pcol = 0
    # Loop through unique pairs
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            # Get column names
            coli = cols[i]
            colj = cols[j]
            # Perform hexbin operation
            plots[prow, pcol].hexbin(df[coli], df[colj], gridsize=20, bins='log')
            # Update title of subplot
            plots[prow, pcol].set(title=f'{coli}-{colj}')

            # Update row and column
            pcol += 1
            if pcol >= sq:
                pcol = 0
                prow += 1
    
    # Set the layout to be tight
    fig.tight_layout()
    
    # Save normalized file if specified
    if norm_output is not None:
        df.to_csv(norm_output, index=False)
    # Save histograms if specified
    if hist_output is not None:
        plt.savefig(hist_output, dpi=200)
    # Show otherwise
    else:
        plt.show()

# if called from command line
if __name__ == '__main__' and len(argv) > 1:
    # Init outputs
    norm_output = None
    hist_output = None
    # read 2nd argument
    if len(argv) > 2:
        norm_output = argv[2]
    # read third argument
    if len(argv) > 3:
        hist_output = argv[3]
    # call main
    main(argv[1], norm_output, hist_output)