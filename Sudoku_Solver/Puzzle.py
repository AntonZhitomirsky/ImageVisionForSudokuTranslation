import numpy
import math
from PIL import Image as PILImage
from Sudoku_Solver import ImageHandling
from Sudoku_Solver import Number
from Sudoku_Solver import List_Handling
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches

class Puzzle:
    def __init__(self, image, template_path):
        # creating a new object so that modifications don't interfere with the original
        self.__puzzle_square = List_Handling.Matrix(image.get_matrix_obj().get_matrix())  # image object -> matrix object
        # initializing number templates
        number_templates = ImageHandling.Image(template_path)
        self.__number_template = Number.Number_Template(number_templates) # number templates
        self.__grid, self.__squares, self.__puzzle = ['list of number Images'], ['list of number Objects object'], \
                                                     ['list of numbers']

    def __split_into_squares(self, dimension=9):
        step_y = int(math.ceil(self.__puzzle_square.get_height() / dimension))
        step_x = int(math.ceil(self.__puzzle_square.get_width() / dimension))
        grid = []
        for y in range(0, self.__puzzle_square.get_height(), step_y):  # stepping through y
            row_of_squares = []
            for x in range(0, self.__puzzle_square.get_width(y), step_x):  # stepping through x
                square = []
                for i in range(step_y):
                    row = []
                    for j in range(step_x):
                        try:  # if this index doesn't exist (due to calling the ceiling function) then skip it
                            row.append(self.__puzzle_square.get_pixel(y+i, x+j))
                        except IndexError:
                            pass
                    if len(row) > 0:
                        square.append(row)
                row_of_squares.append(square)
            grid.append(row_of_squares)
        return grid

    def __is_empty(self, square, border):
        # steps into the image,  1/border of the original size
        # so 1/4 will form a margin that is 1/4 the size of the original
        sum = 0
        step = int(len(square)/border)
        for y in range(step, len(square) - step):
            for x in range(step, len(square[y]) - step):
                sum = sum + square[y][x]
        sum = sum / ((len(square)-2*step)*((len(square[0]))-2*step))
        if sum > 235:
            return True
        else:
            return False

    def __extract_number_objects(self, border=4):
        numbers = List_Handling.Number_list([])
        for y in range(9):
            for x in range(9):
                if not self.__is_empty(self.__grid[y][x], border):
                    refined_squares = numpy.asarray(self.__grid[y][x])
                    position = (x, y)
                    image = ImageHandling.Image(refined_squares)
                    number = Number.Number(image, self.__number_template, position)
                    number.optimize_num()
                    number.calculate_number()
                    numbers.append(number)
        return numbers

    def __form_puzzle(self):
        return_list = []
        for x in range(9):
            row = []
            for y in range(9):
                trigger, index = self.__squares.contains_position((y, x))
                if trigger:
                    row.append(self.__squares.get_number(index))
                else:
                    row.append(0)
            return_list.append(row)
        return return_list

    def get_puzzle_matrix(self):
        return List_Handling.Matrix(self.__form_puzzle())

    def normalise_image(self, corners):
        total = 0

        # calculating the rotation angle
        for i in range(4):
            coord1 = corners[i % 4]
            coord2 = corners[(i + 1) % 4]
            angle = math.atan2((coord2[1] - coord1[1]), (coord2[0] - coord1[0]))
            angle = 360 * angle / (2 * math.pi)
            total = total + angle

        if total >= 0:
            total = total - 180
        elif total < 0:
            total = total + 180

        average = total / 4
        average_rad = average * math.pi / 180

        new_corners = []

        # calculating the rotated coordinates in relation to the centre coordinates
        for coordinate in corners:
            # coordinates relative to the centre
            old_coordinate_y = coordinate[1] - self.__puzzle_square.get_height() / 2
            old_coordinate_x = coordinate[0] - self.__puzzle_square.get_width() / 2
            # radius of the point from the centre
            radius = math.sqrt(math.pow(old_coordinate_y, 2) + math.pow(old_coordinate_x, 2))
            phi = math.atan2(old_coordinate_y, old_coordinate_x)
            angle_after = phi - average_rad
            # new coordinates
            new_coordinate_h = self.__puzzle_square.get_height() / 2 + radius * math.sin(angle_after)
            new_coordinate_w = self.__puzzle_square.get_width() / 2 + radius * math.cos(angle_after)
            new_corners.append((new_coordinate_w, new_coordinate_h))

        # rotating
        img = PILImage.fromarray(numpy.asarray(self.__puzzle_square.get_matrix()))
        rotated = img.rotate(average)

        # cropping
        h_min, h_max, w_min, w_max = List_Handling.get_width_and_height(new_corners)
        normalised = rotated.crop((int(w_min), int(h_min), int(w_max), int(h_max)))

        self.__puzzle_square._update_matrix(numpy.asarray(normalised.convert('L')))

    def get_image_matrix(self):
        return self.__puzzle_square.get_matrix()

    def process_puzzle(self):
        self.__grid = self.__split_into_squares()  # splitting the image into squares, regardless if it is empty
        self.__squares = self.__extract_number_objects()  # gets rid of empty squares
        self.__puzzle = self.__form_puzzle()  # creates a list of integers specifying location of numbers

    def add_number(self, number, position):
        trigger, index = self.__squares.contains_position(position)
        if 0 < number < 10 and not trigger:
            number_template = self.__number_template.get_image(number)  # returns an ImageHandling.Image object
            number_template = Number.Number(number_template, None, position, number=number)
            #number_template.optimize_num()

            # obtaining coordinates from position
            height_of_square = int(math.ceil(self.__puzzle_square.get_height() / 9))
            width_of_square = int(math.ceil(self.__puzzle_square.get_width() / 9))
            coordinates = (int(width_of_square * (position[0] + 0.15)), int(height_of_square * (position[1] + 0.15)))

            # resizing
            number_template = Number.Number(number_template._resize_height(0.7*height_of_square), None, position, number=number)

            # pasting this into the image
            image = ImageHandling.Image(self.__puzzle_square.get_matrix())
            image_to_paste = ImageHandling.Image(number_template.get_image().get_matrix_obj().get_matrix())
            image = image.add_element(image_to_paste, coordinates[0], coordinates[1])

            self.__puzzle_square = List_Handling.Matrix(image.get_matrix_obj().get_matrix())#.convert("L"))

            self.__squares.append(number_template)
        #else:
        #    raise Exception('either number is out of range, or a number already exists at that position')
