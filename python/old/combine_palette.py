import os
import sys

# Main function
def main(dirname):
    # Go through each file
    for filename in os.listdir(dirname):
        if filename.endswith('.csv'):
            name = filename[:-4] + ','
            # Open file
            with open(os.path.join(dirname, filename)) as csv:
                while True:
                    line = csv.readline()
                    if not line:
                        break
                    line = line.rstrip()
                    if len(line) > 0:
                        # Print the name of the file, then append other csv fields
                        print(name + line)


if __name__ == '__main__' and len(sys.argv) > 1:
    main(sys.argv[1])