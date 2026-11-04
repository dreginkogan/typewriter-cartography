from Map import Map
from PIL import Image
Image.MAX_IMAGE_PIXELS = 300000000
import numpy as np
import matplotlib.pyplot as plt


map_instance = Map("cropped_allegheny.tif")
print(map_instance.dims)

map_instance.crop_to_paper(center=(map_instance.dims[0] // 2, map_instance.dims[1] // 2), orientation='portrait', primary_dim=10000, paper='letter')
# map_instance.to_typewriter_map(orientation='portrait', width=7.5)
print(map_instance.dims)

# map_instance.to_typewriter_map(orientation='landscape', width=15, levels=8)
map_instance.to_typewriter_map(orientation='landscape', width=7.5, levels=5)

print(map_instance.dimensions)

image = np.array(map_instance.geo_data)

Image.fromarray(image.astype(np.uint8)).save("output/test_image.png")
