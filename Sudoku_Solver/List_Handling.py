import math
import numpy

def get_width_and_height(array):
    y_max = -math.inf
    x_max = -math.inf
    x_min = math.inf
    y_min = math.inf
    for coordinate in array:
        if y_max < coordinate[1]:
            y_max = coordinate[1]
        if x_max < coordinate[0]:
            x_max = coordinate[0]
        if y_min > coordinate[1]:
            y_min = coordinate[1]
        if x_min > coordinate[0]:
            x_min = coordinate[0]
    return y_min, y_max, x_min, x_max


class Stack:
    def __init__(self, initial_list):
        self.__stack = initial_list

    def get_length(self):
        return len(self.__stack)

    def get_top(self):
        return self.pop(remove=False)

    def pop(self, remove=True):
        try:
            item = self.__stack[len(self.__stack) - 1]
            if remove:
                self.__stack.remove(item)
            return item
        except IndexError:
            return None

    def push(self, obj):
        self.__stack.append(obj)

    def get_stack(self):
        return self.__stack

    def set_stack(self, new_stack):
        self.__stack = new_stack

    def get_top_n_numbers(self, n):
        if n <= self.get_length():
            return self.__stack[self.get_length() - n:self.get_length()]
        else:
            return self.get_stack()


class Number_list:
    def __init__(self, list):
        self.__list = list

    def append(self, object):
        self.__list.append(object)

    def get_number(self, position):
        try:
            return self.__list[position].get_number()
        except IndexError:
            raise Exception("not in list")

    def get_position(self, position):
        try:
            return self.__list[position].get_position()
        except IndexError:
            raise Exception("not in list")

    def contains_position(self, position):
        for i in range(len(self.__list)):
            if self.__list[i].get_position() == position:
                return True, i
        return False, 0

    def get_len(self):
        return len(self.__list)


class Matrix:
    def __init__(self, matrix):
        self.__matrix = numpy.asarray(matrix)

    def get_width(self, y=0):
        # it is an assumption that all of the rows in the image are the same length
        return len(self.__matrix[y])

    def get_height(self):
        return len(self.__matrix)

    def get_pixel(self, x, y):
        return self.__matrix[x][y]

    def get_matrix(self):
        return numpy.asarray(self.__matrix)

    def _update_matrix(self, new_matrix):
        self.__matrix = new_matrix
