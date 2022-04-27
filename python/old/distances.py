from sys import argv

# Evaluates if a value can be cast to a float
def is_float(n):
    try:
        test = float(n)
        return True
    except ValueError:
        return False

# This is simply L2 norm, I will not take square root for efficiency
def CLD_dist(a,b):
    # Convert to float
    a = [float(n) for n in a if is_float(n)]
    b = [float(n) for n in b if is_float(n)]
    # Get boundary (min shared)
    bound = min(len(a), len(b))
    dist_sq = 0 # Start keeping track of distance
    #Standard L2 Norm
    for i in range(bound):
        dist_sq+=(a[i]-b[i])**2
    # I don't feel the need to take the square root - too expensive
    return dist_sq

# This was taken from implementation (Bilvideo)
def HTD_dist(a,b):
    a = [float(n) for n in a if is_float(n)]
    b = [float(n) for n in b if is_float(n)]
    radial = 5
    angular = 6
    max = 9237

    dist = 0
    wm = [0.42,1.00,1.00,0.08,1.00]
    wd = [0.32,1.00,1.00,1.00,1.00]

    a = a[2:]
    b = b[2:]

    for n in range(radial):
        for m in range(angular):
            i1 = n*angular+m
            dist += wm[n]*abs(a[i1] - b[i1])
            i2 = i1+30
            dist += wd[n]*abs(a[i2] - b[i2])
    return dist/max

# TODO other distances here

# Analyze both provided files in the order (CLD, HTD)
def main(path1, path2):
    top = 3 # Take the top 3 similar
    # Set up header
    header = 'type'
    footer = ''
    for i in range(top):
        header+=f',dist_top{i},images_top{i}'
        footer+=f',dist_bot{top-i},images_bot{top-i}'
    header += footer
    # Print header
    print(header)
    # Evaluate CLD
    helper(path1, CLD_dist, 'CLD', top)
    # Evaluate HTD
    helper(path2, HTD_dist, 'HTD', top)

# There is a little bit of repeated code between this and greatest
# TODO
def helper(path, dist, row_name, top):
    with open(path) as f: # Open file
        lines = f.readlines() # Read all lines
        split = ' ' # Constant for what to split on
        data = [s.strip().split(split) for s in lines] # Split lines
        lines = None # Remove this from memory
        bound = len(data) # Find # of rows
        tuples = [] # Begin keeping track of tuples
        # Iterate half of the combination matrix
        for i in range(bound): 
            for j in range(i+1,bound):
                # Safety check for the read line
                if len(data[i]) > 1 and len(data[j]) > 1:
                    # Combined name
                    name = f'{data[i][0]}_{data[j][0]}'
                    # Append name and distance
                    tuples.append( (name, dist(data[i][1:], data[j][1:])) )
        
        # Safety check (maybe remove this?)
        if len(tuples) > top:
            # Sort pairings
            tuples.sort(key=lambda x: x[1])
            # Set up printing information
            s = row_name
            sf = ''
            # Find the top and bottom X
            for i in range(top):
                s += f',{tuples[i][1]},{tuples[i][0]}'
                fi = len(tuples)-(i+1)
                sf += f',{tuples[fi][1]},{tuples[fi][0]}'
            s += sf
            # Print information
            print(s)

if __name__ == '__main__' and len(argv) > 2:
    main(argv[1], argv[2])