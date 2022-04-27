import pandas as pd
from sys import argv

# Join two csvs on the image column
def main(in1, in2, output):
    csv1 = pd.read_csv(in1, sep=',') # Read csv 1
    csv2 = pd.read_csv(in2, sep=',') # Read csv 2
    csvo = csv1.merge(csv2, on='image') # Merge on image
    csvo.to_csv(output, index=False) # Save output

# If this is called from the command line
if __name__ == '__main__' and len(argv) > 3:
    main(argv[1], argv[2], argv[3])