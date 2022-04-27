from pathlib import Path
import numpy as np
from sys import argv

# Various extensions that are supported
extensions = ['png', 'jpg', 'jpeg']

# Main method
def main(path):
    # For each extension
    for extension in extensions:
        # Search for matching files within the parent (recursive)
        for match in Path(path).rglob('*.' + extension):
            print(str(match))

# If this is called from the command line
if __name__ == '__main__' and len(argv) > 1:
    main(argv[1])