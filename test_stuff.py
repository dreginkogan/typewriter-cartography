from Map import Map
from PIL import Image
Image.MAX_IMAGE_PIXELS = 300000000
import numpy as np
import matplotlib.pyplot as plt


map_instance = Map("cropped_allegheny.tif")

map_instance.crop_to_paper_aspect(center=(map_instance.dims[0] // 2, map_instance.dims[1] // 2), orientation='landscape', primary_dim=15000, paper='letter')

map_instance.to_typewriter_array(orientation='landscape', type_width=7.5, levels=5)

typewriter_map = map_instance.to_typewriter_map(mode="rgb")

typewriter_map.save("output/test_image.png")

