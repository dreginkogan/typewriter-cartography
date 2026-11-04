from PIL import Image
Image.MAX_IMAGE_PIXELS = 300000000 # Increase the maximum number of pixels allowed for images
import numpy as np

class Map:

    # init with PIL image
    def __init__(self, geo_data):
        """
        Initialize the Map class with geographical data.
        
        Parameters:
        geo_data (class 'PIL.TiffImagePlugin.TiffImageFile'): A dictionary containing geographical data.
        """
        self.geo_data = geo_data
        self.dims = geo_data.size

    # init with file path
    def __init__(self, filepath):
        """
        Initialize the Map class with a file path to a geographical image.
        
        Parameters:
        filepath (str): The path to the geographical image file.
        """
        self.geo_data = Image.open(filepath)
        self.dims = self.geo_data.size # PIL does width, height, as opposed to the usual Python convention

    def crop_to_paper(self, center, orientation, primary_dim, paper="letter"):
        """
        Crop the geographical image to the specified region.
        
        Parameters:
        center (tuple): The center coordinates of the crop box.
        orientation (str): The orientation of the crop box ('portrait' or 'landscape').
        primary_dim (int): The primary dimension of the crop box in pixels, depending on the orientation.
        paper(str): The paper size to use for cropping. Default is "letter". Other sizes include "a4" and "a3".

        Returns:
        Map: A new Map instance with the cropped image.
        """
        paper = paper.lower()
        # can update with more sizes in the future, but I think this is fine for now.
        aspect_ratios = {
            "letter": 279 / 216,
            "a4": 297 / 210,
            "a3": 420 / 297
        }

        if orientation == 'portrait':
            width = primary_dim
            height = int(width * aspect_ratios[paper])  # Maintain specified paper aspect ratio
        elif orientation == 'landscape':
            height = primary_dim
            width = int(height * aspect_ratios[paper])
        else:
            raise ValueError("Orientation must be 'portrait' or 'landscape'")

        left = center[0] - width // 2 # using // instead of / to round to int
        upper = center[1] - height // 2
        right = center[0] + width // 2
        lower = center[1] + height // 2

        cropped_image = self.geo_data.crop((left, upper, right, lower))
        self.geo_data = cropped_image
        self.dims = self.geo_data.size
        return self

    def to_typewriter_map(self, orientation, width, levels=4, water_threshold=0.2, horizontal_keys_per_inch=10, vertical_keys_per_inch=6):
        """
        Convert the geographical image to a typewriter map.

        Parameters:
        orientation (str): The orientation of the typewriter map ('portrait' or 'landscape').
        width (int): The width of the map in inches that will be typed on the typewriter, remember to leave margins.
        levels (int): The number of height levels to use for the typewriter map. Default is 4.
        water_theshold (float): The 'value' under which a pixel gets registered as being water
        horizontal_keys_per_inch (float): The number of horizontal keys per inch.
        vertical_keys_per_inch (float): The number of vertical keys per inch.

        Returns:
        Map: A new Map instance with the typewriter map.
        """

        #todo, fix how dimensions are scaled for portrait vs landscape

        # width is how wide on the page when printing
        #orientation refers to the orientation of the paper to display the map properly (in landscape, the map will be printed sideways)
        if orientation == 'portrait': # same way it is printed, same way it is displayed
            width = int(width * horizontal_keys_per_inch)
            height = int(width * vertical_keys_per_inch / horizontal_keys_per_inch)
        elif orientation == 'landscape':
            height = int(width * vertical_keys_per_inch)
            width = int(height * horizontal_keys_per_inch / vertical_keys_per_inch)
        else:
            raise ValueError("Orientation must be 'portrait' or 'landscape'")


        scaled_image = self.geo_data.resize((width, height), resample=3)
        image_array = np.array(scaled_image)

        height_min = np.min(image_array)
        height_max = np.max(image_array)

        print(height_min, height_max)

        image_array -= height_min
        image_array /= (height_max - height_min)
        image_array *= levels # what the sigma do i multiply by
        image_array[image_array==4.0] = 3.0

        binned_image_array = image_array.astype(np.uint8) # sometimes acts weird

        print(np.min(binned_image_array),np.max(binned_image_array), np.mean(binned_image_array))

        # need a better way of dealing with water
        water_negative = np.zeros_like(image_array)
        water_negative[image_array > water_threshold] = 1 #1

        binned_image_array+=water_negative.astype(np.uint8) 

        self.geo_data = Image.fromarray(binned_image_array.astype(np.uint8)*int(255/levels))
        self.dimensions = self.geo_data.size
        self.typewriter_arr = image_array
        return self