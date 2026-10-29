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

paper_size = (97, 75) #temporary, 

resampled_size = paper_size#(round(im.size[0]*0.75), round(im.size[1]*0.75))

im = im.resize(resampled_size, resample=3)

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
        if imarray[i,j] > 5:
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