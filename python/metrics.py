from sys import argv
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import math

import traceback
import matplotlib.pyplot as plt

# Find metrics for the given text file, containing image paths
# Skipping pat for now
def main(txt):
    # header = 'image,br_avg,br_std,pat,comp'
    header = 'image,brightness_average,brightness_deviation,compression,patterns'
    print(header)
    for line in txt:
        name = line.strip()
        try:
            img = cv2.imread(name)
            bright = get_lstar(img)
            avg = np.average(bright)
            std = np.std(bright)
            # Just in case
            pat = 0
            try:
                pat = get_pat(img)
            except Exception:
                # Do not interrupt
                pass
            comp = get_comp(img)
            # Format string too
            result = [name]
            result += [f'{val:.8f}' for val in [avg, std, comp, pat]]
            print(','.join(result))
        except Exception:
            # print(traceback.format_exc())
            continue
    # Done

# Gets LAB brightness
# (This was partially copy-pasted from pattern-coverage)
def get_lstar(img):
    # img = np.float32(img) # Convert to correct format
    # bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # Convert to BGR
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB) # BGR2LAB
    return lab[:,:,0] # Grab just the L* (brightness)

def get_pat(img):
    # Obtain data and point pairings
    data, points = get_points(img)
    # Get pattern pairings
    pairs = match_pat(img, data, points)
    # Fill in the image based on pattenrs found
    rect_img = draw_rects(img, data, pairs)
    # Get percentage of image covered by patterns
    # DEBUG get_rects_display(rect_img)
    coverage = np.count_nonzero(rect_img) / np.prod(rect_img.shape)
    # Return the result
    return coverage

'''
def debug_pat(points):
    count = 0
    for i in range(len(points)):
        count += len(points[i])
    maxPoints = 30
    if count > maxPoints:
        print("BAD BAD BAD")
    else:
        print("v")
'''

def get_points(img):
    # Threshold constant
    thresh = 0.5
    # Shortcut for threshold squared (for square comparison)
    thresh_sq = thresh*thresh
    # Create a SIFT generator with max features
    sift = cv2.SIFT_create()
    # Obtain SIFT features
    kp, desc = sift.detectAndCompute(img, None)

    # Init each list with its own index
    points = [[i] for i in range(len(desc))]
    
    # Never add a point more than once
    checked = [False for i in range(len(desc))]

    # Only one side of the digaonal
    for i in range(len(desc)):
        if (checked[i]):
            continue
        for j in range(i+1, len(desc)):
            if not checked[j] and desc[i].shape == desc[j].shape:
                diff = (desc[i]-desc[j])
                dist_sq = np.sum(diff**2)
                if dist_sq < thresh_sq:
                    points[i].append(j)
                    checked[j] = True # Update checked
    
    # Filter
    points = [arr for arr in points if len(arr) > 1]
    # Sort with highest first
    points.sort(key=lambda x : len(x), reverse=True)
    # Maximum number of points
    maxPoints = 30
    count = 0
    cutoff = 0
    while cutoff < len(points):
        count += len(points[cutoff])
        if count > maxPoints:
            break
        cutoff+=1
    points = points[:cutoff] # Cut the points off at a reasonable number
    # Return data and point indices in a similarity 2d array
    return kp, points

# For debugging
def get_points_display(img, data, points):
    out = img.copy()
    for i in range(len(points)):
        # Find color (smooth hue)
        arr = np.reshape([255*i/len(points),1,1],newshape=(1,1,3))
        arr = np.float32(arr)
        color = cv2.cvtColor(arr, cv2.COLOR_HSV2BGR)[0,0]
        color = tuple([int(255*c) for c in color])
        # Get relevant keypoints
        dtg = [data[p] for p in points[i]]
        # Draw relevant keypoints
        cv2.drawKeypoints(out, dtg, out, color=color)
    plt.imshow(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
    plt.show()

# Also for debugging
def get_rects_display(rect_img):
    plt.imshow(rect_img)
    plt.show()

# Gets pairings between points with shared relationships
def match_pat(img, data, points):
    pats = []
    # Iterate types of points
    for i in range(len(points)):
        # Only check one side of the diagonal
        for j in range(i+1, len(points)):
            # print(f'Displaying groupings for: ({i},{j})')
            # Get the normalized result
            norm = normalize_all(data, points[i], points[j])
            # get_norm_display(norm)
            # Group by size
            groups = compare_norm(norm, lambda x : x[0].size, None)
            # get_groups_display(img, data, groups)
            # Check groups by x
            groups = compare_norm(norm, lambda x: x[0].pt[0], groups)
            # get_groups_display(img, data, groups)
            # Check groups by y
            groups = compare_norm(norm, lambda x: x[0].pt[1], groups)
            # get_groups_display(img, data, groups)
            #print('---')
            # Remove keypoint context
            if len(groups) > 0:
                pats.append([ [(c[1],c[2]) for c in g] for g in groups])
    return pats

def get_groups_display(img, data, groups):
    # Line color constant
    color = (0,0,0)
    # Init drawing image
    out = img.copy()
    # Print data
    # print(groups)
    # Keypoint array to draw
    kp = []
    for g in groups:
        for tup in g:
            # Keypoints
            kp1 = data[tup[1]]
            kp2 = data[tup[2]]
            # Line between them
            cv2.line(out,
                [int(c) for c in kp1.pt],
                [int(c) for c in kp2.pt],
                color)
            # Append Keypoints for later drawing
            if kp1 not in kp:
                kp.append(kp1)
            if kp2 not in kp:
                kp.append(kp2)
    print([k.pt for k in kp])
    cv2.drawKeypoints(out, kp, out)
    # Convert to rgb for matplotlib
    out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
    # Draw image in pyplot
    plt.imshow(out)
    # Show result
    plt.show()

def kp_str(kp):
    return f'x:{kp.pt[0]}, y:{kp.pt[1]}, scale:{kp.size}, angle:{kp.angle}'

def get_norm_display(norm):
    print([f'kp: {kp_str(tup[0])}, a: {tup[1]}, b: {tup[2]}' for tup in norm])

# Normalizes all points in b to each point in a
def normalize_all(data, a, b):
    # Init empty matrix
    norm = [None for _ in range(len(a)*len(b))]
    k = 0
    # Iterate through a
    for i in range(len(a)):
        # Iterate through b
        for j in range(len(b)):
            # Normalize the pairing
            norm[k] = normalize_point(data, a[i], b[j])
            k+=1
    # Return the result
    return norm

# Normalizes d2 as if d1 was the center of the universe
def normalize_point(data, ai, bj):
    # Data
    d1 = data[ai]
    d2 = data[bj]

    # Angle diff
    angle = (d2.angle - d1.angle)

    # Size ratio
    size = d2.size / d1.size

    # Center accordingly
    dx = (d2.pt[0] - d1.pt[0]) / d1.size
    dy = (d2.pt[1] - d1.pt[1]) / d1.size

    # Rotation information + updates
    rad = math.radians(angle)
    angle = angle % 360
    sin = math.sin(rad)
    cos = math.cos(rad)

    # Get final coordinates
    x = dx*cos - dy*sin
    y = dx*sin + dy*cos

    # Return the created point
    return (cv2.KeyPoint(x,y,size,angle), ai, bj)

# I would use indicies but it becomes to hard to follow in terms of readability
def compare_norm(norm, fcn, sets):
    # Shortcut optimization
    if sets is not None and len(sets) == 0:
        return sets
    
    # Set up threshold constants
    thresh = 0.1

    # Sort norm
    norm.sort(key=fcn)

    # Init new sets
    new_sets = []

    curr = None

    for i in range(len(norm)-1):
        # Check adjacencies
        if abs(fcn(norm[i]) - fcn(norm[i+1])) <= thresh:
            if curr is None:
                curr = [norm[i], norm[i+1]]
            else:
                curr.append(norm[i+1])
        # Pattern broken
        elif curr is not None:
            new_sets.append(curr)
            curr = None
    # Append last set
    if curr is not None:
        new_sets.append(curr)
    # Check against sets
    if sets is not None:
        # Put each set in order
        for s in sets:
            s.sort(key=fcn)
        # Put sets array in order
        sets.sort(key=lambda x: fcn(x[0]))
        # Linear search through both
        i = 0
        j = 0
        k = 0
        l = 0
        final_sets = []
        curr = None
        # Must be in the bounds for both sets
        while i < len(sets) and j < len(new_sets):
            # Debug: print(f'i:{i},j:{j},k:{k},l:{l}')
            # Indices must be in the range of their respective sets
            if k >= len(sets[i]):
                i+=1
                k = 0
            elif l >= len(new_sets[j]):
                j+=1
                l = 0
                # Attempt to append current
                if curr is not None:
                    final_sets.append(curr)
                    curr = None
            else:
                # Comparison points
                c1 = sets[i][k]
                c2 = new_sets[j][l]
                # Eval
                f1 = fcn(c1)
                f2 = fcn(c2)
                # Same val
                if f1 == f2:
                    # Find same point
                    if c1 is c2:
                        if curr is None:
                            curr = [c1]
                        else:
                            curr.append(c1)
                        # Only inc k if matched
                        k+=1
                    l+=1
                elif f1 < f2:
                    k += 1
                else:
                    j += 1
        # Last append
        if curr is not None:
            final_sets.append(curr)
        # Return intersection
        return final_sets

    # Simply return the new sets
    return new_sets

# Pairs is a 2d array of (point1, point2)
def draw_rects(img, data, pairs):
    # Connections
    conn = [[] for _ in range(len(data))]
    # First dim is class pairs
    for cp in pairs:
        # Second dim is groupings in class pairs
        for g in cp:
            # Third dim is points within the grouping
            for p in g:
                conn[p[0]].append(p[1])
                conn[p[1]].append(p[0])
    # Track what is visited
    visit = np.zeros(shape=(len(data)))
    # Set up rectangles
    rects = []
    # Get boundaries of image for simplification
    bound_x = img.shape[1]
    bound_y = img.shape[0]
    # Find all rectangles
    for i in range(len(visit)):
        if visit[i] == 0:
            find_rect(data, conn, visit, rects, i, bound_x, bound_y)
    # Get image
    rect_img = np.zeros(shape=(img.shape[0], img.shape[1]))
    for rect in rects:
        rect_img[rect[0]:rect[1], rect[2]:rect[3]] = 1
    return rect_img
    
# Gets the bounds of a given rect via BFS
def find_rect(data, conn, visit, rects, i, bound_x, bound_y):
    # Set up queue
    queue = [i]
    # Set up bounds
    min_x = None
    max_x = None
    min_y = None
    max_y = None
    while len(queue) > 0:
        node = queue.pop(0)
        if visit[node] == 0:
            visit[node] = 1
            node_data = data[node]

            # TODO updated code here
            node_min_x = node_data.pt[0] - node_data.size
            node_max_x = node_data.pt[0] + node_data.size
            node_min_y = node_data.pt[1] - node_data.size
            node_max_y = node_data.pt[1] + node_data.size

            # Update bounds
            if min_x is None or node_min_x < min_x:
                min_x = node_min_x
            elif max_x is None or node_max_x > max_x:
                max_x = node_max_x

            if min_y is None or node_min_y < min_y:
                min_y = node_min_y
            elif max_y is None or node_max_y > max_y:
                max_y = node_max_y
            
            # Update what to search next
            queue += conn[node]
    
    # Append a new rectangle if valid
    if (min_x is not None and max_x is not None and min_x < max_x
        and min_y is not None and max_y is not None and min_y < max_y):
        # Adjust and floor
        if min_x < 0:
            min_x = 0
        else:
            min_x = math.floor(min_x)
        if max_x > bound_x:
            max_x = bound_x
        else:
            max_x = math.floor(max_x)
        if min_y < 0:
            min_y = 0
        else:
            min_y = math.floor(min_y)
        if max_y > bound_y:
            max_y = bound_y
        else:
            max_y = math.floor(max_y)
        # Changed the order because of the relationship with rows and cols
        rects.append( (min_y, max_y, min_x, max_x) )
        
# Gets a ratio on how compressable the image provided is
def get_comp(img):
    # Quality constant
    quality = 50
    # Format constant
    format = 'jpeg'
    # Convert to PIL
    pimg = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2LAB) )
    # Object to save to
    out = BytesIO()
    # Perform compression
    pimg.save(out, format=format,quality=quality)
    # Original memory the image used
    mem_old = np.prod(img.shape)
    # New memory, after compression
    mem_new = out.getbuffer().nbytes
    # Safety
    if mem_old == 0:
        mem_old = 1
    # Return calculation
    return 1 - (mem_new/mem_old)

# If used on the command line
if __name__ == '__main__' and len(argv) > 1:
    with open(argv[1]) as f:
        main(f.readlines())
else:
    main('resources/test_imgs.txt')