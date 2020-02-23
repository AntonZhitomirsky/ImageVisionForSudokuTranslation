from Sudoku_Solver import ImageHandling
from Sudoku_Solver import Puzzle

sudoku_image_path = r'C:\Users\anton\OneDrive\Desktop\CS Project\testing\TestImages\rotated_online.jpg'
template_path = r'C:\Users\anton\OneDrive\Desktop\CS Project\testing\number_template.jpg'

image = ImageHandling.Image(sudoku_image_path)
image.compress(compression_ratio=1, dynamic_size=5, divisor=3)
image.print_image()
# getting border and normalizing image

# extracting numbers from grid
sudoku = Puzzle.Puzzle(image, template_path)
sudoku.normalise_image()

normalised_image = ImageHandling.Image(sudoku.get_image_matrix())
normalised_image.print_image()

sudoku.process_puzzle()


def print_puzzle(puzzle):
    for x in range(puzzle.get_height()):
        for y in range(puzzle.get_width()):
            print(puzzle.get_pixel(x, y), ' ', end='')
        print()


print_puzzle(sudoku.get_puzzle_matrix())
print()
for i in range(9):
    sudoku.add_number(1, (i, 0))


#new_list = sudoku.get_image_matrix()
#ImageHandling.Image(new_list).print_image()
#print_puzzle(sudoku.get_puzzle_matrix())
