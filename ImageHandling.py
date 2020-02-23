from PIL import Image as PILImage
import numpy
import requests
from Sudoku_Solver import List_Handling
from io import BytesIO
#from urllib2 import urlopen


class Image:
    # dynamic_size, into how many parts the image is split for dynamic thresholding
    # the dimensions of an n by n square where all the pixels are combined and averaged
    def __init__(self, image_data):
        try:
            self.path = image_data
            image_data = self.__get2Darray()  # translating to a 2D array
        except AttributeError:
            # if image_data is an array:
            self.path = None
        self.__matrix = List_Handling.Matrix(image_data)

    def __get2Darray(self):
        try:
            response = requests.get(self.path)
            im = PILImage.open(BytesIO(response.content))
        except ValueError:  # invalid URL
            im = PILImage.open(self.path)
        return numpy.asarray(im.convert('L'))

    def __compress(self, dimensions_h, dimensions_w):
        """
        :param dimensions_h:
        :param dimensions_w:
        where the dimensions are the sizes of the square that will traverse the image
        When the dimensions don't divide into the height or the width, the remaining pixels are added up and the average
        is taken, thus handling this exception
        :return: compressed matrix : Type, array of integers
        """
        compressed_matrix = []
        try:
            for h1 in range(0, self.__matrix.get_height(), dimensions_h):  # stepping through height
                width_ways = []
                d_height = dimensions_h
                for w1 in range(0, self.__matrix.get_width(), dimensions_w):  # stepping through weight
                    total = 0
                    d_width = dimensions_w
                    # calculating whether or not the filter goes off the bounds of the image
                    if h1 + d_height > self.__matrix.get_height():
                        d_height = self.__matrix.get_height() - h1
                    for h2 in range(d_height):  # stepping through secondary height
                        # calculating whether or not the filter goes off the bounds of the image
                        if w1 + d_width > self.__matrix.get_width():
                            d_width = self.__matrix.get_width() - w1
                        for w2 in range(d_width):  # stepping through secondary width
                            total = total + self.__matrix.get_pixel(h1 + h2, w1 + w2)  # appending values to unified pixel
                    average = total / (d_width * d_height)
                    width_ways.append(int(average))
                compressed_matrix.append(width_ways)
            return compressed_matrix
        except IndexError:
            raise Exception('incorrect Index')

    def __exaggerate_pixels(self, threshold, matrix):
        """
        if pixel > threshold then white (white = 255)
        there's no reason for me to store grey pixels, I only care about data that's there or not
        therefore if average value of pixels is above a threshold, i can count that as a black pixel
        :param threshold:
        :param matrix: either a single value or a 2D list of integers
        :return: either a value or a refined 2D list of 255 and 0s

        """
        try:
            # if a single value is passed into matrix
            if int(matrix) > threshold:
                return 255
            else:
                return 0
        except TypeError:
            # if a list is passed into matrix
            compressed_matrix = matrix.copy()
            for i in range(matrix.get_height()):  # going through height
                for j in range(matrix.get_width()):  # going through width
                    if matrix[i][j] > threshold:
                        compressed_matrix[i][j] = 255
                    else:
                        compressed_matrix[i][j] = 0
            return compressed_matrix

    def __dynamic_exaggerate_pixels(self, pixel_list, threshold_list, split_h, split_w, divisor):
        """
        refines the image into a number of black and white pixels.
        :param pixel_list: 2D array
        :param threshold_list: 2D array
        :param split_h:
        :param split_w:
        :param divisor:
        :return: returns a 2D array
        """
        #  copying the list so I can directly access memory without having to append values
        new_matrix = pixel_list.copy()
        for h in range(len(pixel_list)):  # stepping through height
            for w in range(len(pixel_list[0])):  # stepping through width
                # calculating the index of the threshold that that pixel should be compared to
                pos_h = int(h / int(numpy.ceil(len(pixel_list) / split_h)))
                pos_w = int(w / int(numpy.ceil(len(pixel_list[0]) / split_w)))
                new_matrix[h][w] = self.__exaggerate_pixels(int(threshold_list[pos_h][pos_w] / divisor),
                                                            new_matrix[h][w])
        return new_matrix

    def compress(self, compression_ratio=1, dynamic_size=1, divisor=1.1):
        """
        calculates the sizes of the large squares which are going to be used to find the dynamic thresholds
        and compresses `the image
        :param compression_ratio:
        :param dynamic_size:
        :param divisor:
        """
        dimension_h = int(numpy.ceil(self.__matrix.get_height() / dynamic_size))
        dimension_w = int(numpy.ceil(self.__matrix.get_width() / dynamic_size))

        # calculating the dynamic threshold list
        dynamic_thresholds = self.__compress(dimension_h, dimension_w)

        # compressing image, removing redundant information
        compressed = self.__compress(compression_ratio, compression_ratio)

        # converting into black and white
        black_and_white = self.__dynamic_exaggerate_pixels(compressed, dynamic_thresholds, dynamic_size, dynamic_size, divisor)

        self.__matrix._update_matrix(black_and_white)

    def print_image(self, save=False, title='print_image'):
        """
        Prints image to screen, optional to save with a name
        :param save:
        :param title:
        :return:
        """
        matrix = numpy.asarray(self.__matrix.get_matrix())  # normalizing array
        img = PILImage.fromarray(matrix)
        img.show('printed_image')
        if save:
            img.save(title, '.jpg')
        # fig, ax = plt.subplots(1)
        # ax.imshow(img)
        # plt.show()

    def get_matrix_obj(self):
        # returns the matrix object
        return self.__matrix

    def add_element(self, image_paste, position_x, position_y):
        """
        Pastes an image onto another image, with coordinates of left top corner (position_x, position_y)
        :param image_paste:
        :param position_x:
        :param position_y:
        :return: the new image object with the image_paste on it
        """
        # pasting this into the image
        im = PILImage.fromarray(self.__matrix.get_matrix())
        im.paste(PILImage.fromarray(image_paste.get_matrix_obj().get_matrix()), (position_x, position_y))
        im = Image(im.convert("L"))
        return im
