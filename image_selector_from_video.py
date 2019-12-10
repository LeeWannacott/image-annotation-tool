import cv2
import numpy as np
import math
import easygui
import sys

# read in video file
cap = cv2.VideoCapture('C:/Users/Lee/Desktop/test_video/GX010223.mp4')

# variables containing default window size.
window_width = 1800
window_height = 1050

# creating background.
#l_img = np.zeros((window_height, window_width, 3), np.uint8)

# original images that that will be resized
initial_img_width = 4000
initial_img_height = 3000


# 9 - 7
number_of_columns = 9
number_of_rows = 7

cell_height = window_height / number_of_rows
#cell_width = window_width / number_of_columns
cell_width = cell_height * (initial_img_width / initial_img_height)
# cell_height = cell_width * (initial_img_height / initial_img_width)
#window_width = int(cell_width * number_of_columns)

print(cell_width)
print(cell_height)

resize_x = cell_width / initial_img_width
resize_y = cell_height / initial_img_height

print(resize_x)
print(resize_y)


# print(cell_height)

# setting up cell widths and asserting cells fit into the window size
# cell_width = initial_img_width * resize_x # 150
# cell_height = initial_img_height * resize_y # 200
assert window_width % cell_width == 0, 'Check that cell_width fits into the windows width'
assert window_height % cell_height == 0, 'Check that cell_height fits into windows height'
# amount of columns, rows and total cells in the grid
# number_of_columns = window_width // cell_width # how many columns there are.
# number_of_rows = window_height // cell_height # how many rows there are.
number_of_cells = number_of_rows * number_of_columns  # number of cells in grid

# global lists
coordinates = []
cell_numbers_temporary = []
cell_numbers_list_for_each_grid = []
frame_numbers_list = []
list_of_frames_to_keep = []
image_list = []
animal_list_temporary = []
animal_list_to_keep = []
animal_list_to_print = []
animal = ''
enable_draw_on_grid = False

# mouse click for left button
def click_event(event, x, y, flags, param):
    global animal
    if event == cv2.EVENT_LBUTTONDOWN and animal == '' and enable_draw_on_grid == True:

        # gets row and column number on left mouse click
        x1 = x
        y1 = y
        col_number = x1 / cell_width
        x1 = math.trunc(col_number)
        row_number = y1 / cell_height
        y1 = math.trunc(row_number)
        # print(x1, y1)
        coordinates.append((x1, y1))

        # get cell number based on coordinates x1,y1
        def coordinate_to_cell(x1, y1):
            # https://stackoverflow.com/questions/9816024/coordinates-to-grid-box-number
            cell_number = int(x1 + (y1 * number_of_columns))
            # Temporary list for drawing rectangles
            cell_numbers_temporary.append(cell_number)
            # cell numbers list for each grid gets cleared by spacebar
            cell_numbers_list_for_each_grid.append(cell_number)
            return cell_number

        cell = coordinate_to_cell(x1, y1)

        # uses the cell number converts to coordinates and draws rectangles
        global newimage
        newimage = param[0].copy()
        image_list.append(newimage)
        def draw_rectangles(cell_number):
            # https://stackoverflow.com/questions/8669189/converting-numbers-within-grid-to-their-corresponding-x-y-coordinates
                x2 = (cell_number) % number_of_columns
                y2 = (cell_number) // number_of_columns
                cell_x_position = x2 * cell_width
                cell_y_position = y2 * cell_height
                draw_to_x = cell_x_position + cell_width
                draw_to_y = cell_y_position + cell_height
                cv2.rectangle(param[0], (int(cell_x_position), int(cell_y_position)), (int(draw_to_x), int(draw_to_y)), (0, 150, 0), 2)
                # print(cell_number)
                cv2.imshow('win', param[0])

        # draw rectangles between two grid images
        def draw_rectangles_span():

            # draws rectangle in the first cell
            if len(cell_numbers_temporary) == 1:
                draw_rectangles(cell)

            if len(cell_numbers_temporary) >= 2:
                between_backwards = list(range(int(cell_numbers_temporary[-1]), int(cell_numbers_temporary[-2] + 1)))  # backwards
                between_forwards = list(range(int(cell_numbers_temporary[-2]), int(cell_numbers_temporary[-1] + 1)))  # forwards
                # draw rectangles backwards
                if cell_numbers_temporary[-1] < cell_numbers_temporary[-2]:
                    for next_cell1 in between_backwards:
                        draw_rectangles(next_cell1)

                # draw rectangles forwards
                if cell_numbers_temporary[-1] > cell_numbers_temporary[-2]:
                    for next_cell2 in between_forwards:
                        draw_rectangles(next_cell2)

                # clear temporary list so another two squares can be selected
                cell_numbers_temporary.clear()

                global animal
                global window_open
                if animal == '':
                    # window_open = True
                    animal = 'window open'
                    animal = easygui.enterbox("What animal is it?")

                # if wanting only integers
                # animal = easygui.integerbox('What animal is it?')

                if animal != 'window open':
                    if animal == None:
                        animal = ''
                    animal_list_temporary.append(animal)
                    animal = ''

        draw_rectangles_span()

    elif event == cv2.EVENT_RBUTTONDOWN and animal == '' and enable_draw_on_grid == True:
                # allows to go back to previously drawn images
        if len(image_list) == 1:
            param[0] = image_list[-1]
            cv2.imshow('win', image_list[-1])
            cv2.waitKey(1)
            image_list.pop()
            cell_numbers_list_for_each_grid.pop()

        elif len(image_list) > 1:
            param[0] = image_list[-2]
            cv2.imshow('win', image_list[-2])
            cv2.waitKey(1)

            image_list.pop()
            image_list.pop()

            cell_numbers_list_for_each_grid.pop()
            cell_numbers_list_for_each_grid.pop()
            if len(animal_list_temporary) > 0:
                animal_list_temporary.pop()


# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")

index = 0
# Read until video is completed
def image_grid(index, x_offset=0, y_offset=0, i=0):
    cap.set(1, index)
    # resetting image to black each time
    l_img = np.zeros((window_height, window_width, 3), np.uint8)
    cv2.imshow('win', l_img)
    cv2.waitKey(1)
    index_for_frame_list = index

    while i < number_of_cells:
        global enable_draw_on_grid
        enable_draw_on_grid = False
        while (cap.isOpened()):
                # Capture frame-by-frame
                ret, frame = cap.read()
                if ret == True:

                    #  resize image
                    s_image = cv2.resize(frame, (0, 0), None, resize_x, resize_y)

                    # put small images onto large image
                    l_img[y_offset:y_offset + s_image.shape[0], x_offset:x_offset + s_image.shape[1]] = s_image
                    # l_img2 = l_img.copy()
                    # show each small images drawn
                    cv2.imshow('win', l_img)
                    cv2.waitKey(1)

                    # prev_image = l_img
                    # i for count of images, index keeps track of where you are in frames
                    i += 1
                    index += 1
                    # lay images into the grid
                    x_offset += int(cell_width)
                    if x_offset == window_width:
                        x_offset = 0
                        y_offset += int(cell_height)
                    if y_offset == window_height:
                        enable_draw_on_grid = True
                        # parameters passed mouse click function
                        param = [l_img, index_for_frame_list]
                        while True:

                            cv2.setMouseCallback('win', click_event, param)
                            c = cv2.waitKey(0)

                            if c == 27: # esc to quite
                                print('Esc pressed to Exit')
                                sys.exit()

                            elif c == 122: # z printing out list of frames that should be kept by the program.
                                pass

                            elif c == 32: # spacebar to go to next images
                                print('Spacebar pressed go to next images')

                                # getting rid of an uneven number of cells in lists
                                if len(cell_numbers_temporary) % 2 == 0:
                                    pass
                                else:
                                    cell_numbers_temporary.pop()
                                if len(cell_numbers_list_for_each_grid) % 2 == 0:
                                    pass
                                else:
                                    cell_numbers_list_for_each_grid.pop()

                               # clears lists for the case of single selected rectangle
                                cell_numbers_temporary.clear()
                                image_list.clear()

                                # creates a animal list from the temporary animal lists of each grid of images.
                                def create_permanent_animal_list():
                                    for animals in animal_list_temporary:
                                        animal_list_to_keep.append(animals)
                                create_permanent_animal_list()


                               # transforms each cell number in the temporary grid into a frame and appends to frame numbers list
                                def each_grid_cells_into_frames_list():
                                    for cell in cell_numbers_list_for_each_grid:
                                        frame_number = int(param[1]) + int(cell)
                                        frame_numbers_list.append(frame_number)
                                each_grid_cells_into_frames_list()

                                print(frame_numbers_list)


                                def make_list_of_frames_to_keep(animal_count=0): # calculates frames spans backwards and forwards
                                    frame_numbers_list_sliced = zip(frame_numbers_list[0::2], frame_numbers_list[1::2])# putting into a list of two's for calculating frame spans
                                    # clear lists on each spacebar; because text file generated on spacebar
                                    list_of_frames_to_keep.clear()
                                    animal_list_to_print.clear()

                                    for numbers in frame_numbers_list_sliced:
                                        # forward frame spans
                                        if numbers[0] < numbers[1]:
                                            for num1 in range(numbers[0], numbers[1] + 1):
                                                list_of_frames_to_keep.append(num1)
                                                animal_list_to_print.append(animal_list_to_keep[animal_count])
                                            animal_count += 1

                                        # backward frame spans
                                        elif numbers[0] > numbers[1]:
                                            for num2 in range(numbers[1], numbers[0] + 1):
                                                list_of_frames_to_keep.append(num2)
                                                animal_list_to_print.append(animal_list_to_keep[animal_count])
                                            animal_count += 1

                                make_list_of_frames_to_keep()

                                # clearing temporary lists, so ready for the next lot of images.
                                cell_numbers_list_for_each_grid.clear()
                                animal_list_temporary.clear()

                                # creating text file with frame numbers and what user tags images as.
                                file = open('List_of_images.txt', 'w')
                                for i, frame in enumerate(list_of_frames_to_keep):
                                    file.write(str(frame) + str(' ' + animal_list_to_print[i]) + '\n')
                                file.close()

                                return image_grid(index)

image_grid(index)

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
