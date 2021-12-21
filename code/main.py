from Sudoku_Processor import ImageHandling
from Sudoku_Processor import Puzzle


# further refined ui by user

sudoku_image_path = r'https://cdn.britannica.com/42/97142-131-E3E24AA5/sudoku-puzzle-games.jpg'
# creating an image object of the puzzle
image = ImageHandling.Image(sudoku_image_path)
# compressing the image object to remove noise and make grey scale
# compression_ratio=None, dynamic_size=5, divisor=1.3
image.compress()
# printing image
image.print_image(save=True, title='compressed')

# creating a puzzle object
sudoku = Puzzle.Puzzle(image)
# processing puzzle will:
# rotate, crop, analyse, form puzzle
sudoku.process_puzzle()
# printing the result of the crop
#sudoku.get_image().print_image()


def print_puzzle(puzzle):
    for x in range(puzzle.get_height()):
        for y in range(puzzle.get_width()):
            print(puzzle.get_item(y, x), ' ', end='')
        print()


# printing console version of puzzle
print_puzzle(sudoku.get_puzzle_matrix())

# adding a bunch of numbers to show image adding capability
print()
for i in range(9):
    for j in range(9):
        sudoku.add_number((i+j) % 9 + 1, (i, j))

# printing image with all 1s added to all empty squares
new_list = sudoku.get_image().print_image()
# printing console version of new puzzle
print_puzzle(sudoku.get_puzzle_matrix())
