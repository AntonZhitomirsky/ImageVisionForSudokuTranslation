from PIL import Image as PILImage
from io import BytesIO
import numpy
import requests
from Sudoku_Processor.List_Handling import Matrix


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
        self.__matrix = Matrix(numpy.asarray(image_data))

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
        When the dimensions doesn't divide into the height or the width, the remaining pixels are added up and the
        average is taken, thus handling the exception if the pixels are out the range of the image
        :return: compressed matrix : Type, array of integers
        """
        compressed_matrix = []
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
                        total = total + self.__matrix.get_item(w1 + w2, h1 + h2)  # appending values to unified pixel
                average = total / (d_width * d_height)
                width_ways.append(int(average))
            compressed_matrix.append(width_ways)
        return compressed_matrix

    def __exaggerate_pixels(self, threshold, matrix):
        """
        if pixel > threshold, then pixel becomes white (white = 255)
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
            for i in range(matrix.get_height()):  # going through height
                for j in range(matrix.get_width()):  # going through width
                    if matrix[i][j] > threshold:
                        matrix[i][j] = 255
                    else:
                        matrix[i][j] = 0
            return matrix

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
        for h in range(len(pixel_list)):  # stepping through height
            for w in range(len(pixel_list[0])):  # stepping through width
                # calculating the index of the threshold that that pixel should be compared to
                pos_h = int(h / int(numpy.ceil(len(pixel_list) / split_h)))
                pos_w = int(w / int(numpy.ceil(len(pixel_list[0]) / split_w)))
                pixel_list[h][w] = self.__exaggerate_pixels(int(threshold_list[pos_h][pos_w] / divisor),
                                                            pixel_list[h][w])
        return pixel_list

    def compress(self, compression_ratio=None, dynamic_size=5, divisor=1.1):
        """
        calculates the sizes of the large squares which are going to be used to find the dynamic thresholds
        and gets rid of redundant information by compressing the image and turning it to black and white
        The compression_ratio is the amount of times that the image is compressed by, aka 2 will half the image's
        resolution.
        :param compression_ratio:
        :param dynamic_size:
        :param divisor:
        """
        if compression_ratio == None:
            compression_ratio = int(numpy.ceil((self.__matrix.get_height()+self.__matrix.get_width())/2000))
            # trying to apply the most optimal compression_ratio, trying to get the resolution down to 1000*1000

        dimension_h = int(numpy.ceil(self.__matrix.get_height() / dynamic_size))
        dimension_w = int(numpy.ceil(self.__matrix.get_width() / dynamic_size))

        # calculating the dynamic threshold list
        dynamic_thresholds = self.__compress(dimension_h, dimension_w)

        # compressing image, removing redundant information
        compressed = self.__compress(compression_ratio, compression_ratio)
        print(compressed[0])
        # converting into black and white (function updates list 'compressed')
        self.__dynamic_exaggerate_pixels(compressed, dynamic_thresholds, dynamic_size, dynamic_size, divisor)

        self.__matrix._update_matrix(compressed)

    def print_image(self, save=False, title='print_image'):
        """
        Prints image to screen, optional to save with a name
        :param save:
        :param title:
        """
        if save:
            self.save(title)
        matrix = numpy.asarray(self.__matrix.get_matrix())  # normalizing array
        img = PILImage.fromarray(matrix).convert("L")
        img.show(title=title)

    def save(self, title):
        matrix = numpy.asarray(self.__matrix.get_matrix())  # normalizing array
        img = PILImage.fromarray(matrix).convert("L")
        title = title + '.jpg'
        img.save(title)

    def get_matrix(self):
        # returns the matrix object
        return self.__matrix.get_matrix()

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
        im.paste(PILImage.fromarray(image_paste.get_matrix()), (position_x, position_y))
        im = Image(im.convert("L"))
        return im

    def resize_height(self, end_height):
        """
        resizes the image with the height being the base and the width being scaled up to maintain the ratio
        :param end_height:
        :return:
        """
        image_object = PILImage.fromarray(self.__matrix.get_matrix())
        baseheight = int(end_height)
        hpercent = (baseheight / float(self.__matrix.get_height()))
        wsize = int((float(self.__matrix.get_width()) * float(hpercent)))
        img = image_object.resize((wsize, baseheight))
        image = Image(img)
        self.__matrix = Matrix(image.get_matrix())
        return image

sudoku_image_path = r'C:\Users\anton\OneDrive\Desktop\documentation\CS Project\testing\TestImages\printed_image_10.jpg'
im = Image(sudoku_image_path)
im.compress()
im.print_image()