from PIL import Image as PILImage
import numpy
import cv2
import math
from Sudoku_Solver import ImageHandling
from Sudoku_Solver import List_Handling


class Number_Template:
    def __init__(self, image_obj):
        self.__number_image = image_obj
        self.__number_image_matrix = List_Handling.Matrix(image_obj.get_matrix_obj().get_matrix())
        self.__number_image.compress(1)
        # pass in an abject with the templates of the numbers
        self.__number_list = self.__split_into_numbers()

        self.number_dictionary = {}

        for i in range(9):
            im = ImageHandling.Image(self.__number_list[i])
            num = Number(im, None, None, i + 1)
            im = num.get_image()
            self.number_dictionary.update({i + 1: im})

    def __split_into_numbers(self):
        # split image evenly to get small images of numbers
        width_divisor = int(self.__number_image_matrix.get_width() / 9)
        number_list = []
        for x in range(0, self.__number_image_matrix.get_width(), width_divisor):
            number = []
            for y in range(0, self.__number_image_matrix.get_height()):
                number.append(self.__number_image_matrix.get_matrix()[y][x:x + width_divisor])
            number_list.append(number)
        return number_list

    def get_image(self, number):
        if 0 < number < 10:
            return self.number_dictionary.get(number)


class Number:
    def __init__(self, image_obj, number_templates, position, number=0):
        # Image object
        self.__number_image = image_obj
        self.__number_image.compress(1)  # getting rid of grey pixels
        self.__repeat = False
        self.__position = position
        self.__number_template = number_templates
        self.__number = number

    def __cut(self, padding_percentage):
        width_step = int(self.__number_image.get_matrix_obj().get_width() * padding_percentage)
        height_step = int(self.__number_image.get_matrix_obj().get_height() * padding_percentage)
        refined_image = []
        for height in range(height_step, self.__number_image.get_matrix_obj().get_height() - height_step):
            refined_image.append(self.__number_image.get_matrix_obj().get_matrix()[height][width_step:
                                                        self.__number_image.get_matrix_obj().get_width() - width_step])
        return self.__cut_out_number(refined_image, False)

    def __cut_out_number(self, refined_image, repeated):
        self.__repeat = False
        refined_image = self.__cut_out_number_vertical(refined_image)
        refined_image = self.__cut_out_number_horizontal(refined_image, repeated)
        # that means that cutting all sides wasn't enough, there was a horizontal or vertical line remaining
        # which stopped the cutting process' efficiency. If True, then it was handled and the process can be finished
        if self.__repeat:
            repeated = True
            return self.__cut_out_number(refined_image, repeated)
        else:
            return refined_image

    def __cut_out_number_horizontal(self, image, repeated):
        cut_out_num_list = []
        first_hit = -1
        last_hit = -1
        for column in range(len(image[0])):
            column_list = []
            for row in range(len(image)):
                column_list.append(image[row][column])
            if column_list.__contains__(0):
                # checks if its likely that there's the remainder of a box surrounding the number
                # if there is this needs to process needs to be repeated again
                if not repeated:
                    if 0.5 * len(column_list) < self.__number_of(column_list, 0) and not (
                            0.1 * len(image[0]) < column < 0.9 * len(image[0])):
                        self.__repeat = True
                    else:
                        if first_hit == -1:
                            first_hit = column
                        cut_out_num_list.append(column_list)
                else:
                    if first_hit == -1:
                        first_hit = column
                    cut_out_num_list.append(column_list)
            elif not repeated and first_hit != -1:
                if first_hit + 10 < column:
                    last_hit = column
                else:
                    first_hit = -1
                    last_hit = -1
            elif repeated and first_hit != -1:
                break
        normalised_list = []
        for y in range(len(cut_out_num_list[0])):
            row = []
            for x in range(len(cut_out_num_list)):
                row.append(cut_out_num_list[x][y])
            normalised_list.append(row)
        return normalised_list

    def __number_of(self, list, item):
        amount = 0
        for i in list:
            if i == item:
                amount = amount + 1
        return amount

    def __cut_out_number_vertical(self, image):
        first_hit = -1
        last_hit = -1
        for row in range(len(image) - 1):
            if image[row].__contains__(0) and first_hit == -1:
                first_hit = row
            # if the next pixel doesn't contain a black pixel
            if (not image[row + 1].__contains__(0)) and ((last_hit == -1) and (first_hit != -1)):
                last_hit = row + 1
            if (last_hit != -1) and (first_hit + 10 > last_hit):
                first_hit = -1
                last_hit = -1
        if last_hit == -1:
            last_hit = len(image)
        cut_out_num_list = []
        for row in range(first_hit, last_hit):
            cut_out_num_list.append(image[row])
        return cut_out_num_list

    def _resize_height(self, height):
        image_object = PILImage.fromarray(numpy.asarray(self.__number_image.get_matrix_obj().get_matrix()))
        baseheight = int(height)
        hpercent = (baseheight / float(image_object.height))
        wsize = int((float(image_object.width) * float(hpercent)))
        img = image_object.resize((wsize, baseheight))
        image = ImageHandling.Image(img)
        return image

    def calculate_number(self, method=cv2.TM_SQDIFF):
        values = []
        method = cv2.TM_SQDIFF
        image = PILImage.fromarray(self.__number_image.get_matrix_obj().get_matrix()).convert("L")
        image.save('temporary.jpg')
        image = cv2.imread('temporary.jpg')
        for i in range(1, 10):
            template = self.__number_template.number_dictionary.get(i).get_matrix_obj().get_matrix()
            template = PILImage.fromarray(numpy.asarray(template)).convert("L")
            template.save('temporary.jpg')
            template = cv2.imread('temporary.jpg')
            thing = cv2.matchTemplate(image, template, method=method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(thing)
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                values.append(min_val)
            else:
                values.append(max_val)

        minimum, maximum = self.__get_min_and_max(values)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            self.__number = values.index(minimum) + 1
        else:
            self.__number = values.index(maximum) + 1

    def get_number(self):
        return self.__number

    def get_position(self):
        return self.__position

    def get_image(self):
        return self.__number_image

    def __get_min_and_max(self, list):
        minimum = math.inf
        maximum = -math.inf
        for number in list:
            if minimum > number:
                minimum = number
            if maximum < number:
                maximum = number
        return minimum, maximum

    def optimize_num(self):
        # cutting away borders and leaving only the number
        self.__number_image = ImageHandling.Image(self.__cut(0.1))
        # resizing the number_image to match the size of the templates
        if self.__number_template != None:
            height = self.__number_template.number_dictionary.get(1).get_matrix_obj().get_height()
            self.__number_image = self._resize_height(height)
            self.__number_image.compress(1)
