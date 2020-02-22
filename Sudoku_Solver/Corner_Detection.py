import numpy
import math
from Sudoku_Solver import List_Handling


class Corner:
    def __init__(self, matrix, step=1, start=1, filter_size=9, threshold_for_complete=5):
        self.__matrix = List_Handling.Matrix(matrix)
        self.__filter_size = filter_size
        self.__step = step
        self.__back_track = List_Handling.Stack([])
        self.__corners = []
        self.__threshold_for_complete = threshold_for_complete
        self.__has_corners = False
        self.__find_corners(start)

    def __propagate_square(self, size):
        """
        extends a square from the top left of the image until a black pixel is detected
        :param size:
        :return: list of coordinates and size of square
        """
        while size <= self.__matrix.get_height() and size <= self.__matrix.get_width():
            hit, coordinates = self.__apply_square(size)
            if hit:
                return coordinates, size
            size = size + self.__step
        return None, None

    def __calc_first_move(self, coordinates):
        """
        with list of coordinates, finds the point closest to the origin as the starting point
        :param coordinates:
        :return: coordinate
        """
        min_len = math.inf
        for coordinate in coordinates:
            length = math.sqrt(math.pow(coordinate[0], 2) + math.pow(coordinate[1], 2))
            if min_len > length:
                min_len = length
                min_coord = coordinate
        return min_coord

    def __apply_square(self, dimension):
        """
        with the current dimension of the large square, finds where there are hits
        :param dimension:
        :return:
        """
        hit = False
        coordinates = []
        for i in range(0, dimension):
            pixel = self.__matrix.get_pixel(i, dimension - 1)
            if pixel == 0:
                hit = True
                coordinates.append((dimension - 1, i))
        for i in range(dimension - 2, -1, -1):
            pixel = self.__matrix.get_pixel(dimension - 1, i)
            if pixel == 0:
                hit = True
                coordinates.append((i, dimension - 1))
        return hit, coordinates

    def __find_corners(self, size):
        """
        propogates the large square until a black pixel is found.
        Once found, the pixel is traversed by a filter until it reaches a conclusion of whether or not it was a dud
        If it was unsuccessful the process starts again with the function calling its self, otherwise, it retrieves corners
        :param size:
        :return:
        """
        self.filter = Filter(self.__filter_size, self.__matrix.get_matrix())
        # all coordinates that the square hit, as well as the size that the dimension was
        coordinates, size_after = self.__propagate_square(size)
        if not(coordinates == None and size_after == None):
            self.__back_track.push(size_after)
            # finds the coordinate from which to start
            coordinate = self.__calc_first_move(coordinates)
            self.filter.set_centre(coordinate)
            self.filter.first_centre = coordinate
            # boolean if the search was a success, therefore found corners
            corners_found = self.filter._traverse(self.__threshold_for_complete)
            if corners_found:
                self.__corners = self.filter.get_corners()
                self.__has_corners = True
            else:
                # continue to traverse with the large square
                self.__find_corners(self.__back_track.pop() + self.__step)

    def get_corners(self):
        return self.__corners

    def has_corners(self):
        return self.__has_corners

class Filter:
    def __init__(self, filter_dimension, matrix):
        self.__matrix = List_Handling.Matrix(matrix)
        if filter_dimension % 2 == 0:
            # if it's even then the centre will be multiple pixels
            raise Exception('variable filter_dimension has to be odd')
        self.dimension = filter_dimension
        self.gap = int((self.dimension - 1) / 2)
        self.centre = (0, 0)
        self.stack_of_centres = List_Handling.Stack([])
        self.vector = (0, 1)
        self.__corners = []
        self.counter = 0
        self.first_centre = (0, 0)

    def __next_centre(self, hits):
        """
        finds the next centre of a list of given coordinates which depends on the vector and where the hits are around
        the square
        :param hits: list of coordinates
        :return: coordinate
        """
        index = -1
        length = 0

        # vector[0] takes priority
        for i in range(4):
            if length < len(hits[i]):
                length = len(hits[i])
            if self.vector.__contains__(i) and len(hits[i]) > 0:
                index = i
                if i == self.vector[0]:
                    break

        if length != 0:
            if (index == -1):# or (index != self.vector[0]):
                # this means that the current vector doesn't work anymore. The vector has to change in order to progress

                self.vector = self.__change_vector()
                return self.__next_centre(hits)
            else:
                # no hits at all
                if length == 0:
                    return True, (1, 1)
                # calculating the next centre by finding midpoint of the appropriate side
                y = 0
                x = 0
                for i in range(len(hits[index])):
                    y = y + hits[index][i][1]
                    x = x + hits[index][i][0]
                y = int(numpy.ceil(y / len(hits[index])))
                x = int(numpy.ceil(x / len(hits[index])))
                return False, (x, y)
        else:
            return True, (1, 1)

    def __change_vector(self):
        if self.vector == (0, 1):
            # right then down
            return (1, 2)
        elif self.vector == (1, 2):
            # down then left
            return (2, 3)
        elif self.vector == (2, 3):
            # left then up
            return (3, 0)
        elif self.vector == (3, 0):
            # up then right
            return (0, 1)

    def _traverse(self, threshold):
        # traverses the edges of the large quadrilateral
        corners_found = True
        while not self.__is_cycle_complete(self.stack_of_centres.get_top(), self.first_centre, threshold):
            noise, self.centre = self.__next_centre(self.__get_hits())
            if noise:
                corners_found = False
                return corners_found
            # checking whether the corners are going back the way they came from
            # n = 20
            # if self.stack_of_centres.get_length() > n and self.__has_backtracked(n):
            #   self.stack_of_centres = Stack(self.stack_of_centres.get_stack()[0:self.stack_of_centres.get_length()
            #                                                                      - n - 1])
            # else:
            self.stack_of_centres.push(self.centre)

        y_min, y_max, x_min, x_max = List_Handling.get_width_and_height(self.stack_of_centres.get_stack())
        if (y_max - y_min < self.__matrix.get_height() / 10 and x_max - x_min < self.__matrix.get_width() / 10) or (
                self.stack_of_centres.get_length() < 20):
            corners_found = False
            return corners_found
        else:
            self.__corners = self.__calculate_corners()
            self.__corners = self.__normalise_corners()
            return corners_found

    def __is_cycle_complete(self, start, end, threshold):
        complete = False
        # cycle is complete if the first pixel and the current centre are fairly close to each other
        # length > 10 so that the output isn't True immediately after start; without it will believe that it has
        # reached the end because the second pixel it looks at is close to the starting pixel
        if self.stack_of_centres.get_length() > 7:
            change_x = math.pow(end[0] - start[0], 2)
            change_y = math.pow(end[1] - start[1], 2)
            number = math.sqrt(change_x + change_y)
            # number < threshold set by the gap size
            if number < threshold * self.gap:
                complete = True

        return complete

    def __get_hits(self):
        # starting at the top left of the filter
        # 0 X 1 1 0
        # 1 0 0 0 1
        # 1 0 C 0 1
        # 1 0 0 0 1
        # 0 1 1 1 0
        # where C is centre, X is starting location and self.dimension = 3
        current = (self.centre[0] - self.gap, self.centre[1] - self.gap - 1)
        hits = []
        side = []
        change_x = 1
        change_y = 0
        # a pixel is traced around a square set by dimension
        for i in range(1, 4 * self.dimension + 1):
            # if pixel is black, then it is a hit
            try:  # if the mask goes out of bounds of the image, it is not going to be a hit, so it is enough to just
                # skip it entirely
                if self.__matrix.get_pixel(current[1],current[0]) == 0:
                    side.append(current)
            except IndexError:
                pass
            if i % self.dimension == 0:
                # then this means that the pixel needs to change direction
                current = (current[0] + change_x, current[1] + change_y)
                temp = change_x
                change_x = change_y
                change_y = temp
                if i % (2 * self.dimension) == 0:
                    change_x = (-1) * change_x
                    change_y = (-1) * change_y
                # if i is divisible by dimension that means that one side has been traced
                hits.append(side)
                side = []
            current = (current[0] + change_x, current[1] + change_y)

        # fig, ax = plt.subplots(1)
        # ax.imshow(image.matrix)
        # marker = patches.Rectangle((self.centre[0], self.centre[1]), 1, 1, linewidth=1, edgecolor='b', facecolor='w')
        # ax.add_patch(marker)
        # for i in range(len(hits)):
        #    for j in range(len(hits[i])):
        #        marker = patches.Rectangle((hits[i][j][0], hits[i][j][1]), 1, 1, linewidth=1, edgecolor='b')
        #        ax.add_patch(marker)
        # plt.show()

        return hits

    def __has_backtracked(self, n):
        list_of_centres = self.stack_of_centres.get_top_n_numbers(n)
        first = list_of_centres[0]
        last = list_of_centres[n-1]
        return self.__is_cycle_complete(first, last, 2)

    def set_centre(self, centre):
        self.centre = centre
        self.stack_of_centres.push(centre)

    def get_corners(self):
        return self.__corners

    def __calculate_corners(self):
        y_min, y_max, x_min, x_max = List_Handling.get_width_and_height(self.stack_of_centres.get_stack())

        x_coords = []
        y_coords = []

        sum_x = 0
        sum_y = 0

        for coordinate in self.stack_of_centres.get_stack():
            x_coords.append(coordinate[0])
            sum_x = sum_x + coordinate[0]
            y_coords.append(coordinate[1])
            sum_y = sum_y + coordinate[1]

        centre_x = int(sum_x / self.stack_of_centres.get_length())
        centre_y = int(sum_y / self.stack_of_centres.get_length())

        # finding index of min and max point
        x_min_index = x_coords.index(x_min)
        x_max_index = x_coords.index(x_max)
        y_min_index = y_coords.index(y_min)
        y_max_index = y_coords.index(y_max)

        coordinates_horizontally_and_vertically = []
        # calculates coordinates either side of the centre
        for coordinate in self.stack_of_centres.get_stack():
            if coordinate[0] + self.gap > centre_x > coordinate[0] - self.gap:
                coordinates_horizontally_and_vertically.append(coordinate)
            if coordinate[1] + self.gap > centre_y > coordinate[1] - self.gap:
                coordinates_horizontally_and_vertically.append(coordinate)

        # avoiding the ZeroDevisionError when the gradient is undefined
        for coordinate in coordinates_horizontally_and_vertically:
            if (coordinate[0] + self.gap > x_max > coordinate[0] - self.gap) or \
                    (coordinate[0] - self.gap < x_min < coordinate[0] + self.gap):
                return [(x_min, y_max), (x_max, y_max), (x_min, y_min), (x_max, y_min)]

        # list of side lines
        top = self.__split_array_with_wraparound(y_max_index, x_min_index, self.stack_of_centres.get_stack())
        bottom = self.__split_array_with_wraparound(y_min_index, x_max_index, self.stack_of_centres.get_stack())
        right = self.__split_array_with_wraparound(x_max_index, y_max_index, self.stack_of_centres.get_stack())
        left = self.__split_array_with_wraparound(x_min_index, y_min_index, self.stack_of_centres.get_stack())

        # equations of the lines
        grad_top, y_intercept_top = self.__linear_regression(self.__split_list(top, 3))
        grad_bottom, y_intercept_bottom = self.__linear_regression(self.__split_list(bottom, 3))
        grad_right, y_intercept_right = self.__linear_regression(self.__split_list(right, 3))
        grad_left, y_intercept_left = self.__linear_regression(self.__split_list(left, 3))

        equations = [(grad_top, y_intercept_top), (grad_right, y_intercept_right), (grad_bottom, y_intercept_bottom)
            , (grad_left, y_intercept_left)]

        # calculating intersections of the 4 equations, which are the corners
        corners = []
        for i in range(4):
            item1 = equations[i % 4]
            item2 = equations[(i + 1) % 4]
            corners.append(self.__find_intercept(item1[0], item1[1], item2[0], item2[1]))
        return corners

    def __linear_regression(self, side):
        sum_x = 0
        sum_y = 0
        sum_xy = 0
        sum_x_squared = 0
        for coordinate in side:
            x = coordinate[0]
            y = coordinate[1]
            sum_x = sum_x + x
            sum_y = sum_y + y
            sum_xy = sum_xy + (x * y)
            sum_x_squared = sum_x_squared + math.pow(x, 2)
        n = len(side)
        gradient = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
        y_intercept = (sum_y - gradient * sum_x) / n
        return gradient, y_intercept

    def __find_intercept(self, gradient1, y_intercept1, gradient2, y_intercept2):
        x = int((y_intercept2 - y_intercept1) / (gradient1 - gradient2))
        y = int(gradient1 * x + y_intercept1)
        return (x, y)

    def __split_list(self, input_list, amount):
        if amount <= 2:
            amount = 3 # to handle the exception; 3 is the minimum value that it can be
        len_of_segment = int(len(input_list) / amount)
        return self.__split_array_with_wraparound(len_of_segment, len(input_list) - len_of_segment, input_list)

    def __split_array_with_wraparound(self, a, b, input_list):
        if a > b:
            return input_list[a:len(input_list) - 1] + input_list[0:b]
        return input_list[a:b]

    def __normalise_corners(self):
        temp_list = self.__corners
        y_min, y_max, x_min, x_max = List_Handling.get_width_and_height(temp_list)
        distances = []
        left_up = 0
        right_down = 0
        # finding distances of corners to origin
        for corner in temp_list:
            distances.append(self.__distance(corner, (0, 0)))
        smallest = math.inf
        largest = 0
        # the largest distance is the bottom right corner
        # the smallest distance is the top left corner
        for i in range(len(distances)):
            if largest < distances[i]:
                largest = distances[i]
                right_down = temp_list[i]
            if smallest > distances[i]:
                smallest = distances[i]
                left_up = temp_list[i]
        temp_list.remove(left_up)
        temp_list.remove(right_down)
        # the remaining corners depend on whether the verified corners contained x_min etc.
        try:
            if left_up[0] != x_min:
                left_down = self.__find_in_array(x_min, temp_list)
            else:
                left_down = self.__find_in_array(y_max, temp_list)

            temp_list.remove(left_down)
            # remaining item by elimination
            right_up = temp_list[0]
            return [left_up, right_up, right_down, left_down]
        except LookupError:
            # if x_min or y_max doesn't exist in the remaining list
            if left_up[1] != y_min:
                right_up = self.__find_in_array(y_min, temp_list)
            else:
                right_up = self.__find_in_array(x_max, temp_list)
            temp_list.remove(right_up)
            left_down = temp_list[0]
            return [left_up, right_up, right_down, left_down]

    def __find_in_array(self, item, array):
        for coordinate in array:
            if coordinate.__contains__(item):
                return coordinate

    def __distance(self, coordinate1, coordinate2):
        try:
            x1 = coordinate1[0]
            y1 = coordinate1[1]
            x2 = coordinate2[0]
            y2 = coordinate2[1]
            return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))
        except TypeError:
            pass
