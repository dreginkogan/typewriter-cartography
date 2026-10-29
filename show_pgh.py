import matplotlib.pyplot as plt
import numpy as np
import PIL

PIL.Image.MAX_IMAGE_PIXELS = 300000000 # 300,000,000
im = PIL.Image.open("cropped_allegheny.tif", )

im_x = im.size[0]
im_y = im.size[1]

crop_box = [0+3700, 0+600, im_x-100, im_y-1000]
im = im.crop(crop_box)

print(im.size)

scaling = 2
paper_size = (97*scaling, 75*scaling) #temporary, 

resampled_size = paper_size#(round(im.size[0]*0.75), round(im.size[1]*0.75))

im = im.resize(resampled_size, resample=3)
# make size paper better match what can fit on the paper -- leave margins. 7.5in x 10 in seems like a good size. 
# 75x60 grid, with each character a 0.6 aspect ratio, need to make image "grid" math these characters.
# the img.show will display it weird as each pixel will be a square, but irl each character is a rectangle and will look better

imarray = np.array(im)

height_min = np.min(imarray)
height_max = np.max(imarray)

print(np.min(imarray), np.max(imarray))

imarray -= height_min

print(np.min(imarray), np.max(imarray))
imarray = np.round(imarray/(height_max-height_min) * 100)

height_0 = np.zeros(imarray.shape)

for i in range(imarray.shape[0]):
    for j in range(imarray.shape[1]):
        if imarray[i,j] > 3: # need to mess around with this value, and also implement smoothing to remove noise
            height_0[i,j] = 0
        else:
            height_0[i,j] = 1

print(np.min(imarray), np.max(imarray))
num_levels = 5
print(np.linspace(0, 100, num_levels+1))
imarray = np.digitize(imarray, np.linspace(0, 100, num_levels+1)) #- 1

plt.imshow(imarray, interpolation='nearest')
plt.show()

plt.imshow(height_0, interpolation='nearest')
plt.show()


#  . + @ $ will use as shades on typewriter

# save the river and elevations as color channels and display as a single image

# make a tool to make phsyically printing on a typewriter from the generated image easier via a grid, etc
# outline rivers in red, use .+@# for elevations
# need a good way to count spaces to reduce the chance of human error on typewriter

# i have to be able to print everything onto the typewriter without having to take out the paper and reorient it
# pittsburgh will have to be printed with the west facing up, given the orientation 