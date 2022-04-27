from matplotlib import pyplot as plt
from sys import argv as args
from scipy.signal import correlate2d as corr2d
import skimage.measure as measure
import numpy as np
import numpy.random as rand
import imageio
import cv2

'''
Hypothesis 1: As more image repetitions are introduced into the file, the higher the result will be
Result: This exhibits a linear positive correlation
'''
def test_hyp1():
    test_scalar = 6 # 5x the pattern size
    num_imgs = np.arange(test_scalar) # How many tests to run
    avg_vals = [hyp_helper(test_scalar, ni) for ni in num_imgs] # Get the average values of each test
    plt.plot(num_imgs, avg_vals) # Plot data
    plt.show() # Show plot

'''
Hypothesis 2: As the image gets bigger, the value should stay the same if it is covered in the same
percentage of repetitions
Result: I cannot interpret this result currently, it seems all over the place
'''
def test_hyp2():
    test_start = 2 # Start with x size
    test_end = test_start+10 # Take x samples
    coverage = .1 # Cover each image with 10% repetitions
    scalars = np.arange(test_start, test_end) # Arrange the x axis
    avg_vals = [hyp_helper(ts, np.round(coverage*ts*ts)) for ts in scalars] # Acquire average values
    plt.plot(scalars, avg_vals) # Plot data
    plt.show() # Show plot

# Makes several images and averages the results of their values
def hyp_helper(test_scalar, test_num):
    num_trial = 3 # How many trials to run?
    # test_px = 100
    # imgs = [get_lstar(make_empty(test_scalar*test_px)) for j in range(num_trial)]
    imgs = [make_test(test_scalar, test_num) for j in range(num_trial)] # Make each image
    vals = [get_val(img) for img in imgs] # Obtain the value for each image
    return np.average(vals) # Average the result

# TODO this is the main metric that this file offers
# Gets this metric on an image
def get_val(img):
    img = get_lstar(img) # Calculate the brightness in lab space
    corr = get_corr(img) # Find the autocorrelation
    flat = corr.ravel() # Flatten the matrix
    pos = flat[flat>=0] # Eliminate negative numbers (Is this the best way to go about this?)
    # Sum all of the data
    return np.sum(pos) / (np.prod(img.shape)) # Account for size of image

# Gets LAB brightness and downsamples the image appropriately
def get_lstar(img):
    img = np.float32(img) # Convert to correct format
    bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # Convert to BGR
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB) # BGR2LAB
    return downsample(lab[:,:,0]) # Downsample and grab just the L* (brightness)

# Autocorrelates an image
def get_corr(img):
    mean = np.mean(img) # Obtain the average
    std = np.std(img)
    if std == 0:
        std = 1
    
    img = (img - mean) / std # Normalize
    # Return the autocorrelation using the same mode
    return corr2d(img, img, mode='same')
    # flat = np.ravel(img)
    # corr = np.correlate(flat, flat, mode='same')
    # print(corr.shape)
    # corr = corr.reshape(img.shape)
    # return corr

# Used to display an arrage of images in pyplot
def display_multiple(imgs):
    f, axarr = plt.subplots(1, len(imgs)) # make an appropriate number of subplots
    for i in range(len(imgs)): # For each image
        axarr[i].imshow(imgs[i]) # Map it to a subplot
    plt.show() # Show the images

# Downsamples an image to a size that can be autocorrelated
def downsample(img):
    target = 144 # Downsample the image to 144px via mean blocks
    # TODO should I apply a Gaussian convolution first?
    # TODO is there a better way of doing this?
    # Debug message
    # print(tuple(np.int32(np.ceil(s/target)) for s in img.shape))
    # Return the downsampling result using block_reduce with np.mean
    return measure.block_reduce(img, block_size=tuple(np.int32(np.ceil(s/target)) for s in img.shape), func=np.mean)

# def make_empty(dim):
#     return np.ones(shape=(dim,dim,4))

# Testing param
test_resource = 'resources/test.png'

# Makes a test image consisting of background noise with a repeated feature
def make_test(test_scalar, test_num):
    img = plt.imread(test_resource) # Get feature
    dim_img = np.max([img.shape[0], img.shape[1]]) # Find largest dimension
    dim_bg = dim_img * test_scalar # Find side length of test image
    bound = dim_bg - dim_img # Where can the repeated feature spawn without cutoff
    bg = rand.rand(dim_bg, dim_bg, 4) # Generate random noise
    # bg = np.full(shape=(dim_bg, dim_bg, 4), fill_value=0.0)
    data = np.zeros(shape=(dim_bg, dim_bg)) # Keep track of where the feature is placed

    placed = 0 # Keep track of amount placed
    # Care for an infinite loop (closer to 100% coverage will loop infinitely in many cases)
    while placed < test_num: # Until the proper amount has been placed
        [x,y] = rand.randint(bound, size=2) # Generate position
        xb = x+img.shape[0] # Get x bound
        yb = y+img.shape[1] # Get y bound
        # Check corners
        if (data[x,y]
            +data[xb, y]
            +data[x,yb]
            +data[xb,yb] == 0):
            
            # If successful

            # Placed increases by 1
            placed+=1
            # Set the section to the image
            bg[x:xb, y:yb] = img
            # Record placement
            data[x:xb,y:yb] = np.ones((img.shape[0], img.shape[1]))
    # Return the generated image
    return bg

def main(txt):
    header = 'image,pattern'
    
    print(header)
    for line in txt:
        image = line.strip()
        try:
            data = imageio.imread(image)
            pattern = get_val(data)
            print(image,pattern)
        except:
            continue
    # Done

# Code if this python file is ran from the command line
if __name__ == '__main__':
    if len(args) > 1:
        with open(args[1]) as f:
            main(f.readlines())
    else:
        test_hyp2()