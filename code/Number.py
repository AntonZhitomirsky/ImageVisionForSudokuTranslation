from PIL import Image as PILImage
import numpy
import cv2
import math
from Sudoku_Processor import ImageHandling
from Sudoku_Processor import List_Handling


class Number_Template:
    def __init__(self, image_obj):
        self.__number_image = image_obj
        self.__number_image.compress(1)
        self.__number_image_matrix = List_Handling.Matrix(image_obj.get_matrix())
        # pass in an abject with the templates of the numbers
        self.__number_list = self.__split_into_numbers()

        self.number_dictionary = {}

        for i in range(9):
            im = ImageHandling.Image(self.__number_list[i])
            num = Number(im, None, None, i + 1)
            num.optimize_num()
            im = num.get_image()
            self.number_dictionary.update({i + 1: im})

    def __split_into_numbers(self):
        """
        split image evenly to get small images of numbers
        :return: list of numbers matrices
        """
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
        self.__number_image_matrix = List_Handling.Matrix(self.__number_image.get_matrix())
        self.__position = position
        self.__number_template = number_templates
        self.__number = number
        self.__repeated = False

    def __cut_out_number(self):
        """
        cuts out numbers widthwise and heightwise
        :return: a matrix object
        """
        # setting the starting positions for the sides of a rectangle that will morph onto the image
        left = int(self.__number_image_matrix.get_width() / 4)
        right = int(3 * self.__number_image_matrix.get_width() / 4)
        up = int(self.__number_image_matrix.get_height() / 4)
        down = int(3 * self.__number_image_matrix.get_height() / 4)
        # setting up the starting directions the rectangle has to move to
        repeated = False
        while True:

            #im = (PILImage.fromarray(self.__number_image_matrix.get_matrix()))
            #fig, ax = plt.subplots(1)
            #ax.imshow(im)

            step_l, step_u, step_d, step_r = -1, -1, 1, 1
            state_before = None
            finished = False
            # checking if borders are inside the image and if the cropping has been complete or not
            while not finished:
                # checking left
                if left > 0:
                    left, step_l = self.__check_side("left", step_l, left, up, down)
                # checking right
                if right < self.__number_image_matrix.get_width() - 1:
                    right, step_r = self.__check_side("right", step_r, right, up, down)
                # checking up
                if up > 0:
                    up, step_u = self.__check_side("up", step_u, up, left, right)
                # checking down
                if down < self.__number_image_matrix.get_height() - 1:
                    down, step_d = self.__check_side("down", step_d, down, left, right)
                # when no more changes are being made, that means that it's found the number, so the loop needs to be broken
                if state_before == (left, right, up, down):
                    finished = True
                state_before = (left, right, up, down)
            #    square = patches.Rectangle((left, up), right - left, down - up, linewidth=1, edgecolor='b',
            #                               facecolor='none')
            #    ax.add_patch(square)
            #plt.show()
            if repeated == True:
                break
            else:
                repeated = True
        return_list = []
        for y in range(up, down):
            return_list.append(self.__number_image_matrix.get_row(y)[left:right + 1])
        return List_Handling.Matrix(return_list)

    def __check_side(self, side, current_direction, current_index, bound_lower, bound_upper):
        # calculating initial direction
        if side in ["right", "down"]:
            initial_direction = 1
        else:
            initial_direction = -1
        # calculating pixels colours that lie on that side
        if side in ["right", "left"]:
            side = self.__number_image_matrix.get_column(current_index)[bound_lower:bound_upper]
        else:
            side = self.__number_image_matrix.get_row(current_index)[bound_lower:bound_upper]
        # calculating next move
        if 0 not in side:
            if current_direction != -initial_direction:
                current_direction = (-1) * current_direction
            current_index = current_index + current_direction
        elif current_direction != -initial_direction:
            current_index = current_index + current_direction
        # returning current side position and current direction
        return current_index, current_direction

    def _resize_height(self, height):
        """
        resizes the image with the height being the base and the width being scaled up to maintain the ratio
        :param height:
        :return:
        """
        image_object = PILImage.fromarray(numpy.asarray(self.__number_image.get_matrix()))
        image = ImageHandling.Image(image_object)
        image.resize_height(height)
        return image

    def calculate_number(self, method=cv2.TM_SQDIFF):
        """
        calculates number by comparing it to all the templates and finding the maximum/minimum value depending on the
        method
        :param method:
        :return: number
        """
        # resizing the number_image to match the size of the templates
        height = List_Handling.Matrix(self.__number_template.number_dictionary.get(1).get_matrix()).get_height()
        self.__number_image = self._resize_height(height)

        values = []
        method = cv2.TM_SQDIFF
        image = PILImage.fromarray(self.__number_image.get_matrix()).convert("L")
        image.save('temporary.jpg')
        image = cv2.imread('temporary.jpg')
        for i in range(1, 10):
            template = self.__number_template.number_dictionary.get(i).get_matrix()
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
        """
        cuts out number and resizes to suit the number templates
        """
        # cutting away borders and leaving only the number
        self.__number_image_matrix = self.__cut_out_number()
        self.__number_image = ImageHandling.Image(self.__number_image_matrix.get_matrix())
