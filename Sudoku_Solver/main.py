from Sudoku_Solver import ImageHandling
from Sudoku_Solver import Corner_Detection
from Sudoku_Solver import Puzzle


sudoku_image_path = r'C:\Users\anton\OneDrive\Desktop\CS Project\testing\TestImages\rotated_online.jpg'
template_path = r'C:\Users\anton\OneDrive\Desktop\CS Project\testing\number_template.jpg'
image = ImageHandling.Image(sudoku_image_path)
image.compress(compression_filter_size=1, dynamic_size=5, divisor=1.5)
#image.print_image()
# getting border and normalizing image

corners = Corner_Detection.Border(matrix=image.get_matrix_obj().get_matrix(), step=1, start=1, threshold_for_complete=5, filter_size=17)



if corners.has_corners():
    # extracting numbers from grid
    sudoku = Puzzle.Puzzle(image, template_path)
    sudoku.normalise_image(corners.get_corners())

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