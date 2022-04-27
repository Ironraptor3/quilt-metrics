import pandas as pd
from sys import argv

# Returns correlation matrix between columns
def main(csv):
    data = pd.read_csv(csv, sep=',') # read file
    corr = data.corr() # get correlation
    result = []
    # Loop through bottom of the diagonal
    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            # Save the name with the result
            result.append((corr.columns[i].strip()+'_'+corr.columns[j].strip(), abs(corr.iloc[i,j]))) # Absolute value (Pearson is [-1,1])
    # Sort to find most related fields
    result.sort(key=(lambda x: x[1]), reverse=True)
    # Print all to stdout
    for r in result:
        print(str(r[0])+','+str(r[1])) # In csv-amenable format

# If called via command line
if __name__ == '__main__' and len(argv) > 1:
    main(argv[1])
