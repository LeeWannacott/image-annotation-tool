
# imports.
import cv2
import numpy as np
import glob
import natsort
import math

# variables containing window size.
window_height = 1050
window_width = 1800

# creating background.
l_img = np.zeros((window_height,window_width,3),np.uint8)

# read in files.
files = glob.glob ("*.jpg")

# sort files into numerical order.
files = natsort.natsorted(files, reverse=False)

# set initial value for get images function.
indexvalue = 0

# allow going back in index.
index_previous_images = []
index_previous_images.append(0)

# original images that that will be resized
initial_img_width = 4000
initial_img_height= 3000

# values used for resizing
resize_x = 0.05
resize_y = 0.05

# setting up cell widths and asserting cells fit into the window size
cell_width = initial_img_width * resize_x # 150
cell_height = initial_img_height * resize_y # 200
assert window_width % cell_width == 0, 'check that cells fit into window width'
assert window_height % cell_height == 0, 'check that cells fit into window height'


number_of_columns = window_width // cell_width # how many columns there are.
number_of_rows = window_height // cell_height # how many rows there are.
number_of_cells = number_of_rows * number_of_columns  # number of cells in grid

coordinates = []
cell_numbers_temporary = []
cell_numbers_list = []


def click_event(event, x, y, flags, l_img, ix=None):
    if event == cv2.EVENT_LBUTTONDOWN:

        # gets row and column number on left mouse click
        x1 = x
        y1 = y
        col_number = x1 / cell_width
        x1 = math.trunc(col_number)
        row_number = y1 / cell_height
        y1 = math.trunc(row_number)
        print(x1, y1)
        coordinates.append((x1,y1))


        # get cell number based on coordinates x1,y1
        def coordinate_to_cell(x1, y1):
            # https://stackoverflow.com/questions/9816024/coordinates-to-grid-box-number
            cell_number = int(x1 + (y1 * number_of_columns))
            cell_numbers_temporary.append(cell_number)
            cell_numbers_list.append(cell_number)
            return cell_number
        cell = coordinate_to_cell(x1,y1)



        # uses the cell number converts to coordinates and draws rectangles
        def draw_rectangles(cell_number):
            # https://stackoverflow.com/questions/8669189/converting-numbers-within-grid-to-their-corresponding-x-y-coordinates
            x2 = (cell_number) % number_of_columns
            y2 = (cell_number) // number_of_columns
            cell_x_position = x2 * cell_width
            cell_y_position = y2 * cell_height
            draw_to_x = cell_x_position + cell_width
            draw_to_y = cell_y_position + cell_height
            cv2.rectangle(l_img, (int(cell_x_position), int(cell_y_position)), (int(draw_to_x), int(draw_to_y)),(0, 150, 0), 2)
            #print(cell_number)
            images_list = cv2.imshow('win', l_img)
            cv2.imshow('win', l_img)
            cv2.waitKey(1)
        # draw_rectangles(cell)


        #draw rectangles between two grid images
        def draw_rectangles_span():
            if len(cell_numbers_temporary) <= 1:
                draw_rectangles(cell)

            elif len(cell_numbers_temporary) >= 2:
                between1 = list(range(int(cell_numbers_temporary[-1]), int(cell_numbers_temporary[-2] + 1)))  # backwards
                between2 = list(range(int(cell_numbers_temporary[-2]), int(cell_numbers_temporary[-1] + 1)))  # forwards
                # draw rectangles backwards
                if cell_numbers_temporary[-1] < cell_numbers_temporary[-2]:
                    for nextone1 in between1:
                        draw_rectangles(nextone1)

                # draw rectangles forwards
                if cell_numbers_temporary[-1] > cell_numbers_temporary[-2]:
                    for nextone2 in between2:
                        draw_rectangles(nextone2)

                # draw rectangles in same square if clicked twice
                if cell_numbers_temporary[-1] == cell_numbers_temporary[-2]:
                    draw_rectangles(cell)
                # clear temporary list so another two squares can be selected
                cell_numbers_temporary.clear()

        draw_rectangles_span()


    elif event == cv2.EVENT_RBUTTONDOWN:
        i=0
        # j=0

    # print(coordinates)

# draws each image into a grid.
def get_images(index,i=0 , y_offset=0, x_offset=0):
    # use current index to create the previous index
    index_previous_images.append(index)
    l_img = np.zeros((window_height, window_width, 3), np.uint8)
    cv2.imshow('win', l_img)
    cv2.waitKey(1)

    for i, s_image in enumerate(files[index:]):
        print(s_image)

        # Read in images and resize them.
        s_image = cv2.imread(s_image)
        s_image = cv2.resize(s_image, (0, 0), None, resize_x, resize_y)  # 4000 * 0.05 = (1800ww / 200image width fits in window 9times), 3000 * 0.05 = (1050wh / 150image height = fits 7 times).

        # Draw small images onto the big images. https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv/14102014#14102014][1]
        l_img[y_offset:y_offset+s_image.shape[0], x_offset:x_offset+s_image.shape[1]] = s_image
        # shows each image sequentially.
        cv2.waitKey(1)
        cv2.imshow('win', l_img)
        x_offset += int(cell_width)
        if x_offset == window_width:
            x_offset = 0
            y_offset += int(cell_height)
        if y_offset == window_height:
            cv2.setMouseCallback('win',click_event,l_img)
            break

    # get index number for next amount of images.
    index_next_images = index + i

    # change images based on key presses
    if cv2.waitKeyEx(0) == 2424832 : # key arrow left pressed twice to go left
        print('left ----------------')
        return get_images(index_previous_images[-2])

    elif cv2.waitKeyEx(0) == 2555904: # key arrow right pressed twice to go right
        print('right ---------------')
        return get_images(index_next_images)

    elif cv2.waitKey(0) == 27: # exit if Escape is hit
        print('Exited --------------')
        cv2.destroyAllWindows()

get_images(indexvalue)