'''
A python file for analyzing all
exported data from the Web Application
'''
from sys import argv
import os

# Main function
def main(path, nameList):
    # Print header
    print(','.join(nameList))
    # For each file in the path
    for binFn in os.listdir(os.fsencode(path)):
        # Get the name
        fn = os.fsdecode(binFn)
        # Get the filepath
        fp = os.path.join(path, fn)
        # Open the file path
        with open(fp) as file:
            # Calculate info
            result = calculateAll(file)
            # Print row
            print(','.join([str(r) for r in result]))

# Save node class
class save:
    # Constructor
    def __init__(self, saves, id, name, parent, data):
        self.id = id
        self.name = name
        self.parent = parent
        # update parent
        if parent in saves:
            saves[parent].children.append(id)
        # init children
        self.children = []
        self.data = data
        # Add to saves
        saves[id] = self
    
    # Str function for debugging
    def __str__(self):
        # Just print id, name, and parent
        return (f'Id: {self.id} Name:{self.name}'
            + f'Parent: {self.parent}')

# Builds saves from a file
def buildSaves(file):
    # Which is selected
    selected = -1
    # Which is the root
    root = None
    # Dictionary of saves
    saves = {}
    # Iterate through file
    for line in file:
        # Remove newline, make array
        line = line.rstrip().split(',')
        # First line encountered
        if selected < 0:
            # Update selected
            # Ignore maxID
            selected = int(line[1])
        # Make a save
        else:
            # Init fields
            id = int(line[0])
            name = line[1]
            parent = int(line[2])
            data = [int(d) for d in line[3:]]
            # Call constructor
            save(saves, id, name, parent, data)
            # If the parent < 0, then it is the root node
            if (parent < 0):
                root = id
    # Return information from file
    return saves, root, selected

# Calculates the number of leaf nodes within the save tree
def numLeaves(saves, root, selected):
    leaves = [node for node in saves.values() if len(node.children) == 0]
    return len(leaves)

# Caculates the total number of nodes within the save tree
def numNodes(saves, root, selected):
    return len(saves)

# Calculates, on average, how much each node is filled
def fillAvg(saves, root, selected):
    count = len(saves) # Num of saves
    if (count == 0): # Prevent div by 0
        return 0
    else:
        sum = 0 # Init sum
        for node in saves.values():
            nonEmpty = [d for d in node.data if d >= 0] # Filter by >= 0 entries
            sum += len(nonEmpty) # Add length of filtered array
        return sum / count

# Calculates, on average, how much each node is filled
def branchAvg(saves, root, selected):
    count = len(saves) # Num of saves
    if (count == 0): # Prevent div by 0
        return 0
    else:
        sum = 0 # Init sum
        for node in saves.values():
            sum += len(node.children) # Count the number of children for the node
        return sum / count

# Gets the depth of the tree recursively
def depth(saves, root, selected):
    node = saves[root] # Selected node
    # List comprehension recursively
    depths = [depth(saves, child, selected) for child in node.children]
    # Get maximum depth
    highest = max(depths, default=0)
    # Return maximum + 1s
    return highest+1

# List of fucntions to call
fcns = [numLeaves, numNodes, fillAvg, branchAvg, depth]
# Headers for the csv file
fcnNames = ['Number of Leaves', 'Number of Nodes', 'Average Fill', 'Average Branches', 'Depth']

# Calculates all functions on the provided file
def calculateAll(file):
    saves, root, selected = buildSaves(file) # Build the saves of the file
    return [fcn(saves,root,selected) for fcn in fcns] # List comprehension function results

# If called from the command line
if __name__ == '__main__' and len(argv) > 1:
    main(argv[1], fcnNames) # Call main on argument 1 with the given csv header