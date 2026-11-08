from PIL import Image
Image.MAX_IMAGE_PIXELS = 300000000 # Increase the maximum number of pixels allowed for images
import numpy as np

class Map:
    #TODO make the annotations/docs here make sense for a CLI tool
    #make dimensions and coords make sense and consistent throughout (PIL and numpy are flipped)
    def __init__(self, geo_data):
        """
        Initialize the Map class with geographical data.
        
        Parameters:
        geo_data (class 'PIL.TiffImagePlugin.TiffImageFile'): A dictionary containing geographical data.
        """
        self.geo_data = geo_data
        self.dims = geo_data.size
        self.aspect = self.dims[0] / self.dims[1]
        self.typewriter_array = None
        self.typewriter_arr_levels = None
        self.typewriter_map = None


    # init with file path
    def __init__(self, filepath):
        """
        Initialize the Map class with a file path to a geographical image.
        
        Parameters:
        filepath (str): The path to the geographical image file.
        """
        self.geo_data = Image.open(filepath)
        self.dims = self.geo_data.size # PIL does width, height, as opposed to the usual Python convention
        self.aspect = self.dims[0] / self.dims[1]
        self.typewriter_array = None
        self.typewriter_arr_levels = None
        self.typewriter_map = None


    def crop_to_paper_aspect(self, center, orientation, primary_dim, paper="letter"):
        """
        Crop the geographical image to the specified region.
        
        Parameters:
        center (tuple): The center coordinates of the crop box. (x, y) [numpy is y x, with y=0 on top (increases down)]
        orientation (str): The orientation of the crop box ('portrait' or 'landscape').
        primary_dim (int): The primary dimension of the crop box in pixels, depending on the orientation.
        paper(str): The paper size to use for cropping. Default is "letter". Other sizes include "a4" and "a3".

        Returns:
        Map: A new Map instance with the cropped image.
        """
        #modifies geo data itself
        paper = paper.lower()
        # can update with more sizes in the future, but I think this is fine for now.
        aspect_ratios = {
            "letter": 279 / 216,
            "a4": 297 / 210,
            "a3": 420 / 297
        }

        if orientation == 'landscape':
            width = primary_dim
            height = int(width / aspect_ratios[paper])  # Maintain specified paper aspect ratio

        elif orientation == 'portrait':
            height = primary_dim
            width = int(height / aspect_ratios[paper])
        else:
            raise ValueError("Orientation must be 'portrait' or 'landscape'")

        left = center[0] - width // 2 # using // instead of / to round to int
        upper = center[1] - height // 2
        right = center[0] + width // 2
        lower = center[1] + height // 2

        cropped_image = self.geo_data.crop((left, upper, right, lower))
        self.geo_data = cropped_image
        self.dims = self.geo_data.size
        self.aspect = self.dims[0] / self.dims[1]
        return self

    def to_typewriter_array(self, orientation, type_width, levels=4, water_threshold=0.2, horizontal_keys_per_inch=10, vertical_keys_per_inch=6):
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

        self.typewriter_arr_levels = levels

        # width is how wide on the page when printing
        #orientation refers to the orientation of the paper to display the map properly (in landscape, the map will be printed sideways)
        if orientation == 'portrait': # same way it is printed, same way it is displayed
            crop_width = int(type_width * horizontal_keys_per_inch)
            crop_height = int(type_width/self.aspect * vertical_keys_per_inch) # points up

        elif orientation == 'landscape': # image is typed sideways 
            crop_width = int(type_width * self.aspect * vertical_keys_per_inch) # points right
            crop_height = int(type_width * horizontal_keys_per_inch)
        else:
            raise ValueError("Orientation must be 'portrait' or 'landscape'")

        scaled_image = self.geo_data.resize((crop_width, crop_height), resample=3)
        image_array = np.array(scaled_image)

        if orientation == 'landscape':
            image_array = np.rot90(image_array, k=3)

        height_min = np.min(image_array)
        height_max = np.max(image_array)

        image_array -= height_min
        image_array /= (height_max - height_min)
        image_array *= levels # what the sigma do i multiply by
        image_array[image_array==4.0] = 3.0

        binned_image_array = image_array.astype(np.uint8) # sometimes acts weird

        # need a better way of dealing with water
        water_negative = np.zeros_like(image_array)
        water_negative[image_array > water_threshold] = 1 

        binned_image_array+=water_negative.astype(np.uint8) 

        self.typewriter_array = binned_image_array
        return self

    def get_typewriter_array(self):
        return self.typewriter_array

    def to_typewriter_map(self, mode='rgb'): # need a better way to name modes/implement them
        # display characters? display colors? both? custom definition?

        if mode=='bw':
            temp_map = Image.fromarray(self.typewriter_array.astype(np.uint8)*int(255/self.typewriter_arr_levels))
            temp_dims = temp_map.size
            temp_map = temp_map.resize((temp_dims[0]*6, temp_dims[1]*10), Image.NEAREST)
        elif mode=='rgb':
            rows = self.typewriter_array.shape[0]
            cols = self.typewriter_array.shape[1]
            temp_arr = np.zeros((rows, cols, 3))
            temp_arr[self.typewriter_array==0, 0] = self.typewriter_arr_levels # this is so jank
            print(self.typewriter_array[self.typewriter_array!=0])
            temp_arr[:, :, 2] = self.typewriter_array# so there can be black
            temp_arr[:, :, 1] = self.typewriter_array

            temp_map = Image.fromarray(temp_arr.astype(np.uint8)*int(255/self.typewriter_arr_levels))
            temp_dims = temp_map.size
            temp_map = temp_map.resize((temp_dims[0]*6, temp_dims[1]*10), Image.NEAREST)

        return temp_map
