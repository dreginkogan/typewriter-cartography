import matplotlib.pyplot as plt
import numpy as np
import PIL
# throws a warning if file is too large (over 178,956,970 pixels)
# allegheny.tif is 3,515,625,000 pixels, i need to find what portion of this is just pittsburgh (what I want)

PIL.Image.MAX_IMAGE_PIXELS = 3515625001 # is this dumb?
im = PIL.Image.open("allegheny.tif", )

print(im.size)
# allegheny.tif is (62,500 x 56,250)

box = (25000, 20000, 45000, 35000)

region = im.crop(box)

region.save("cropped_allegheny.tif")

# imarray = np.array(region)
# print(imarray.shape)

# plt.imshow(imarray, interpolation='nearest')
# plt.show()
