import random
import numpy as np
import math
from PIL import Image

class ProjectorImage():
    def __init__(self, size_x, size_y, cell_size = 15):
        self.size_x = size_x
        self.size_y = size_y
        self.cell_size = cell_size
        self.raw_array = None

        self.COLORS_RGB = {
            "r": np.array([255,   0,   0], dtype=np.uint8),
            "g": np.array([  0, 255,   0], dtype=np.uint8),
            "b": np.array([  0,   0, 255], dtype=np.uint8),
            "B": np.array([  0,   0,   0], dtype=np.uint8),
            "W": np.array([255, 255, 255], dtype=np.uint8),
        }
        self.COLORS_RGB565 = {
            "r": self._rgb2rgb565(self.COLORS_RGB["r"]),
            "g": self._rgb2rgb565(self.COLORS_RGB["g"]),
            "b": self._rgb2rgb565(self.COLORS_RGB["b"]),
            "B": self._rgb2rgb565(self.COLORS_RGB["B"]),
            "W": self._rgb2rgb565(self.COLORS_RGB["W"]),
        }
        self.COLOR_INDEXES = {"r": 0, "g": 1, "b": 2, "B": 3, "W": 4 }
        self.COLOR_INDEXES_REVERSE = ["r","g","b","B","W"]

        nr_of_pixels    = math.ceil((self.cell_size - 1)) ** 2

        self.pixels = np.array(self._create_rnd_distribution([
            (self.COLOR_INDEXES["W"], 0.34),
            (self.COLOR_INDEXES["B"], 0.66),
        ], nr_of_pixels), dtype=np.uint8)


    def _create_rnd_distribution(self, values, min_results=1):
        min_multiplier = int(1 / min([v[1] for v in values]))
        for multiplier in range(min_multiplier, 102):
            mvalues = [v[1] * multiplier for v in values]
            is_all_int = [mvalue - int(mvalue) < 0.0001 for mvalue in mvalues]
            if all(is_all_int) == True and sum(mvalues) >= min_results:
                r = []
                for index, mvalue in enumerate(mvalues):
                    r.extend([values[index][0]] * int(mvalue))
                random.shuffle(r)
                return r

    def create(self):
        self.raw_array = np.zeros((self.size_x, self.size_y), dtype=np.uint8)
        self.raw_array.fill(self.COLOR_INDEXES["B"] )
        for pos_x in range(0, self.size_x - self.cell_size + 1 , self.cell_size):
            for pos_y in range(0, self.size_y-self.cell_size + 1, self.cell_size):
                self._create_cell(pos_x, pos_y)

    def get_img(self):
        if self.raw_array is None:
            self.create()
        arr = np.zeros((self.size_y, self.size_x, 3), dtype=np.uint8)
        for pos_x in range(0, self.size_x):
            for pos_y in range(0, self.size_y):
                arr[pos_y, pos_x] = self.COLORS_RGB[self.COLOR_INDEXES_REVERSE[self.raw_array[pos_x, pos_y]]]
        img = Image.fromarray(arr, 'RGB')
        return img

    def get_fb(self):
        if self.raw_array is None:
            self.create()
        arr = np.zeros((self.size_y, self.size_x, 2), dtype=np.uint8)
        for pos_x in range(0, self.size_x):
            for pos_y in range(0, self.size_y):
                arr[pos_y, pos_x] = self.COLORS_RGB565[self.COLOR_INDEXES_REVERSE[self.raw_array[pos_x, pos_y]]]
        return bytes(arr)

    def _create_cell(self, pos_x, pos_y):
        np.random.shuffle(self.pixels)

        index = 0
        index_border = 0
        for i in range(1, self.cell_size, 1):
            for j in range(1, self.cell_size, 1):
                self.raw_array[pos_x + i ][pos_y + j ]  = self.pixels[index]
                index += 1

        # LEFT
        for i in range(self.cell_size):
            self.raw_array[pos_x][pos_y + i] = self.COLOR_INDEXES["W"]
            index_border += 1
        # RIGHT
        #for i in range(self.cell_size):
        #    self.raw_array[pos_x+self.cell_size-1][pos_y +  i] = self.border_pixels[index_border]
        #    index_border += 1
        # TOP
        for i in range(self.cell_size):
            self.raw_array[pos_x+ i][pos_y ] = self.COLOR_INDEXES["W"]
            index_border += 1
        # BOTTOM
        #for i in range(self.cell_size):
        #    self.raw_array[pos_x+ i][pos_y + self.cell_size-1] = self.border_pixels[index_border]
        #    index_border += 1

    def _rgb2rgb565(self,rgb):
        r, g, b = rgb
        return np.array([(g & 0x1c) << 3 | (b >> 3), r & 0xf8 | (g >> 3)], dtype=np.uint8)

class ProjectorImage_new():
    def __init__(self, size_x, size_y, cell_size=15):
        self.size_x = size_x
        self.size_y = size_y
        self.cell_size = cell_size
        self.raw_array = None

        self.COLORS_RGB = {
            "r": np.array([255,   0,   0], dtype=np.uint8),
            "g": np.array([  0, 255,   0], dtype=np.uint8),
            "b": np.array([  0,   0, 255], dtype=np.uint8),
            "B": np.array([  0,   0,   0], dtype=np.uint8),
            "W": np.array([255, 255, 255], dtype=np.uint8),
        }
        self.COLORS_RGB565 = {
            "r": self._rgb2rgb565(self.COLORS_RGB["r"]),
            "g": self._rgb2rgb565(self.COLORS_RGB["g"]),
            "b": self._rgb2rgb565(self.COLORS_RGB["b"]),
            "B": self._rgb2rgb565(self.COLORS_RGB["B"]),
            "W": self._rgb2rgb565(self.COLORS_RGB["W"]),
        }
    def _rgb2rgb565(self,rgb):
        r, g, b = rgb
        return np.array([(g & 0x1c) << 3 | (b >> 3), r & 0xf8 | (g >> 3)], dtype=np.uint8)

    def _set_random_pixel_value(self, arr, x, y):
        if x%self.cell_size == 0 or y%self.cell_size==0: # grid
            return
        if x > 0 and y > 0:
            proposed_value = random.choice([0,0,0, 255, 255])
            if (arr[x-1, y] == arr[x, y-1] == arr[x-1, y-1] == proposed_value): # top, left
                arr[x, y] = 0 if proposed_value == 255 else 255
            elif (arr[x+1, y] == arr[x, y-1] == arr[x+1, y-1] == proposed_value == 255): # top, right
                arr[x, y] = 0 if proposed_value == 255 else 255
            elif (arr[x + 1, y] == arr[x, y + 1] == arr[x + 1, y + 1] == proposed_value == 255):  # bottom, right
                arr[x, y] = 0 if proposed_value == 255 else 255
            elif (arr[x - 1, y] == arr[x, y + 1] == arr[x - 1, y + 1] == proposed_value == 255):  # bottom, left
                arr[x, y] = 0 if proposed_value == 255 else 255
            else:
                arr[x, y] = proposed_value
        else:
            arr[x, y] = random.choice([0,0,0, 255, 255])

    def create(self):
        arr = np.zeros((self.size_x, self.size_y), dtype=int)
        # grid
        for x in range(self.size_x-1):
            for y in range(self.size_y-1):
                if x % self.cell_size == 0 or y % self.cell_size == 0:
                    arr[x, y] = 255
        for x in range(self.size_x-1):
            for y in range(self.size_y-1):
                self._set_random_pixel_value(arr, x, y)
        return arr

    def get_img(self):
        if self.raw_array is None:
            self.raw_array = self.create()
        arr = np.zeros((self.size_y, self.size_x, 3), dtype=np.uint8)
        for pos_x in range(0, self.size_x):
            for pos_y in range(0, self.size_y):
                arr[pos_y, pos_x] = [0,0,0] if self.raw_array[pos_x, pos_y] == 0 else [255, 255, 255]
        img = Image.fromarray(arr, 'RGB')
        return img

    def get_fb(self):
        if self.raw_array is None:
            self.raw_array = self.create()
        arr = np.zeros((self.size_y, self.size_x, 2), dtype=np.uint8)
        for pos_x in range(0, self.size_x):
            for pos_y in range(0, self.size_y):
                arr[pos_y, pos_x] = arr[pos_y, pos_x] = self.COLORS_RGB565["B"] if self.raw_array[pos_x, pos_y] == 0 else self.COLORS_RGB565["W"]
        return bytes(arr)



if __name__ == "__main__":
    c = ProjectorImage_new(1920, 1080, 11)
    img = c.get_img()
    img.show()
    #fb = c.get_fb()
    #print(fb)