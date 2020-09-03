import cv2
import numpy as np
import math
import easygui
import sys

''' 
This program has been designed for use in a machine learning - data science context; to speed up image selection.

Program designed for reading in images from a video resizing the original images down into a grid and allowing 
the user to select a span of images and tag the images with text. A text file containing the frame numbers and tagging 
is produced on each press of the space bar; New images are also fed into the grid on Space bar.

Esc = Exit the program.
Left mouse click = Select span of images.
Right mouse click = Undo image span selection.
Space bar = Go to next set of images and store tagged images + frame number in text file.
'''

# ************************************************************************
# variables that can be change by the user:

# Select file path to read video file from.
cap = cv2.VideoCapture('C:\\Users\\Lee\\Desktop\\image-selector-opencv-python\\video.mp4')

# Number of rows is changeable value. Default value is 7.
number_of_rows = 7

# Variables containing default window size for the grid - default values assume 1080p.
window_width = 1800
window_height = 1050

# Original images from video that will be resized down to fit into grid.
initial_img_width = 1920
initial_img_height = 1080

# ************************************************************************

# Calculating how many frames are in the video useful for last image grid.
frames_in_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('Frames in video: ' + str(frames_in_video))


def recalculate_window_stuff():
    global cell_height
    global cell_width
    global number_of_cells
    global number_of_columns
    global number_of_rows
    global resize_x
    global resize_y
    global window_height
    global window_width
    (_, _, temp_window_width, temp_window_height) = cv2.getWindowImageRect('image_selector_from_video')
    if not (temp_window_width == -1 or temp_window_height == -1):
        window_width = temp_window_width
        window_height = temp_window_height
    print(f"Window size: {window_width}x{window_height}")

    cell_height = window_height // number_of_rows
    cell_width = int(cell_height * (initial_img_width / initial_img_height))

    # cell_aspect_ratio and image_aspect_ratio used for assert statement; for debugging.
    cell_aspect_ratio = cell_width / cell_height
    image_aspect_ratio = initial_img_width / initial_img_height
    assert abs(
        cell_aspect_ratio - image_aspect_ratio) < 0.01, f"cell_aspect_ratio={cell_aspect_ratio} image_aspect_ratio={image_aspect_ratio}"

    number_of_columns = window_width // cell_width
    resize_x = cell_width / initial_img_width
    resize_y = cell_height / initial_img_height
    number_of_cells = number_of_rows * number_of_columns
    print('Cell width: ' + str(cell_width), 'Cell Height: ' + str(cell_height),
          'Number of rows: ' + str(number_of_rows),
          'Number of Columns: ' + str(number_of_columns))


# Global lists
coordinates = []
cell_numbers_temporary = []
cell_numbers_list_for_each_grid = []
frame_numbers_list = []
list_of_frames_to_keep = []
image_list = []
image_list_for_bounding_boxes = []
image_list_temporary = []
image_list_to_keep = []
image_list_to_print = []
image = ''
enable_draw_on_grid = False
new_image = ''
bounding_box_start_coordinates_x_y = ()
last_mouse_button_clicked = []
drawn_one_cell_or_span = []
list_of_bounding_box_coordinates = []
temporary_list_of_cells_that_have_bounding_boxes = []
temp_dict_cell_number_and_bounding_boxes = {}
perm_dict_cell_number_and_bounding_boxes = {}

# Mouse click for left button
def click_event(event, x, y, flags, param):
    global image
    global last_mouse_button_clicked
    global bounding_box_start_coordinates_x_y
    global new_image
    global image_list_for_bounding_boxes
    global drawn_one_cell_or_span
    global list_of_bounding_box_coordinates
    global temporary_list_of_cells_that_have_bounding_boxes
    global temp_dict_cell_number_and_bounding_boxes
    global perm_dict_cell_number_and_bounding_boxes

    if event == cv2.EVENT_LBUTTONDOWN and image == '' and enable_draw_on_grid == True:
        last_mouse_button_clicked.append('left')
        # Gets row and column number on left mouse click
        col_number = x / cell_width
        x1 = math.trunc(col_number)
        row_number = y / cell_height
        y1 = math.trunc(row_number)

        # Get cell number based on coordinates x1, y1
        def coordinate_to_cell(x, y):
            # https://stackoverflow.com/questions/9816024/coordinates-to-grid-box-number
            cell_number = int(x + (y * number_of_columns))
            # Temporary list for drawing rectangles

            cell_numbers_temporary.append(cell_number)
            # cell numbers list for each grid gets cleared by space
            cell_numbers_list_for_each_grid.append(cell_number)
            return cell_number

        # For use in drawing rectangle function.
        cell = coordinate_to_cell(x1, y1)

        # Making copy of image for undo function.
        new_image = param[0].copy()
        image_list.append(new_image)

        # Uses the cell number converts to coordinates and draws rectangles
        def draw_rectangles(cell_number):
            # https://stackoverflow.com/questions/8669189/converting-numbers-within-grid-to-their-corresponding-x-y-coordinates
            x2 = cell_number % number_of_columns
            y2 = cell_number // number_of_columns

            cell_x_position = x2 * cell_width
            cell_y_position = y2 * cell_height

            draw_to_x = cell_x_position + cell_width
            draw_to_y = cell_y_position + cell_height
            # print(x2,y2,cell_x_position,cell_y_position,draw_to_x,draw_to_y)
            cv2.rectangle(param[0], (int(cell_x_position), int(cell_y_position)), (int(draw_to_x), int(draw_to_y)),
                          (0, 150, 0), 2)
            cv2.imshow('image_selector_from_video', param[0])

        # draw rectangles between two grid images
        def draw_rectangles_span():

            # Draws rectangle in the first cell
            if len(cell_numbers_temporary) == 1:
                draw_rectangles(cell)
                drawn_one_cell_or_span.append('one')

            if len(cell_numbers_temporary) >= 2:
                between_backwards = list(
                    range(int(cell_numbers_temporary[-1]), int(cell_numbers_temporary[-2] + 1)))  # backwards
                between_forwards = list(
                    range(int(cell_numbers_temporary[-2]), int(cell_numbers_temporary[-1] + 1)))  # forwards
                # Draw rectangles backwards
                if cell_numbers_temporary[-1] < cell_numbers_temporary[-2]:
                    for next_cell1 in between_backwards:
                        draw_rectangles(next_cell1)

                # Draw rectangles forwards
                if cell_numbers_temporary[-1] > cell_numbers_temporary[-2]:
                    for next_cell2 in between_forwards:
                        draw_rectangles(next_cell2)

                # Clear temporary list so another two squares can be selected
                cell_numbers_temporary.clear()

                drawn_one_cell_or_span.append('span')
                global image
                global window_open
                if image == '':
                    # Window_open = True
                    image = 'window open'
                    image = easygui.enterbox("What is tagged in the images?")
                    # replace
                    if image is not None:
                        image = image.replace(" ","")

                if image != 'window open':
                    if image is None:
                        image = ''
                    image_list_temporary.append(image)
                    image = ''

        draw_rectangles_span()

    elif event == cv2.EVENT_MBUTTONUP and image == '' and enable_draw_on_grid == True and len(
            last_mouse_button_clicked) > 0 and last_mouse_button_clicked[-1] == 'left':

        # Allows going back to previously drawn images

        if len(image_list) >= 1 and drawn_one_cell_or_span[-1] == 'one':
            param[0] = image_list[-1]
            cv2.imshow('image_selector_from_video', image_list[-1])
            cv2.waitKey(1)
            image_list.pop()
            cell_numbers_list_for_each_grid.pop()
            last_mouse_button_clicked.pop()
            drawn_one_cell_or_span.pop()

            cell_numbers_temporary.clear()

        elif len(image_list) >= 2 and drawn_one_cell_or_span[-1] == 'span':
            param[0] = image_list[-2]
            cv2.imshow('image_selector_from_video', image_list[-2])
            cv2.waitKey(1)

            # Popping lists to undo selection span of images
            image_list.pop()
            image_list.pop()

            last_mouse_button_clicked.pop()
            last_mouse_button_clicked.pop()

            drawn_one_cell_or_span.pop()
            drawn_one_cell_or_span.pop()

            cell_numbers_list_for_each_grid.pop()
            cell_numbers_list_for_each_grid.pop()

            if len(image_list_temporary) > 0:
                image_list_temporary.pop()

    elif event == cv2.EVENT_MBUTTONUP and enable_draw_on_grid == True and len(last_mouse_button_clicked) > 0 and last_mouse_button_clicked[-1] == 'right':
        if len(image_list) >= 1 and last_mouse_button_clicked[-1] == 'right':
            param[0] = image_list[-1]
            cv2.imshow('image_selector_from_video', image_list[-1])
            cv2.waitKey(1)

            image_list.pop()
            last_mouse_button_clicked.pop()
            # Allows for the potential to have multiple boundary boxes in same cell
            if len(temp_dict_cell_number_and_bounding_boxes[temporary_list_of_cells_that_have_bounding_boxes[-1]]) > 4:

                # Removing four coordinates if more than one boundary box in cell.
                for i in range(4):
                    del temp_dict_cell_number_and_bounding_boxes[temporary_list_of_cells_that_have_bounding_boxes[-1]][-1]

            # Removes boundary boxes if in a single cell
            elif len(temp_dict_cell_number_and_bounding_boxes[temporary_list_of_cells_that_have_bounding_boxes[-1]]) == 4:
                temp_dict_cell_number_and_bounding_boxes.pop(temporary_list_of_cells_that_have_bounding_boxes[-1])


            # Removes cell number from temporary list
            temporary_list_of_cells_that_have_bounding_boxes.pop()

    # Allow bounding boxes to be places over images
    elif event == cv2.EVENT_RBUTTONDOWN and len(drawn_one_cell_or_span) > 0 and drawn_one_cell_or_span[-1] == 'span':

        def get_bounding_box_start_coordinates(x, y):
            x_start_boundary = x
            y_start_boundary = y
            # Calculates starting cell number
            col_number = x / cell_width
            x1 = math.trunc(col_number)
            row_number = y / cell_height
            y1 = math.trunc(row_number)
            cell_number_on_start_of_drawing = int(x1 + (y1 * number_of_columns))


            return x_start_boundary, y_start_boundary, cell_number_on_start_of_drawing

        bounding_box_start_coordinates_x_y = get_bounding_box_start_coordinates(x, y)


    elif event == cv2.EVENT_RBUTTONUP and len(drawn_one_cell_or_span) > 0 and drawn_one_cell_or_span[-1] == 'span':
        # Get cell number at end of bounding box
        col_number = x / cell_width
        cell_x = math.trunc(col_number)
        row_number = y / cell_height
        cell_y = math.trunc(row_number)
        cell_number_on_end_of_drawing = int(cell_x + (cell_y * number_of_columns))
        # Minus x,y positions to get cells relative position
        cell_x_position = cell_x * cell_width
        cell_y_position = cell_y * cell_height

        def draw_boundary_box(x, y, start_boundary_x_and_y):
            # Making copy for un-drawing bounding box
            new_image_boundary = param[0].copy()
            image_list.append(new_image_boundary)

            # Draws bounding box
            end_boundary_x_and_y = (x, y)
            cv2.rectangle(param[0], (start_boundary_x_and_y[0], start_boundary_x_and_y[1]),
                          (end_boundary_x_and_y[0], end_boundary_x_and_y[1]), (0, 150, 150), 2)
            cv2.imshow('image_selector_from_video', param[0])

            # Used for un-drawing bounding box logic
            last_mouse_button_clicked.append('right')

            # Makes the coordinates relative to within that cell rather than the whole window.
            cell_start_relative_position_x = start_boundary_x_and_y[0] - cell_x_position
            cell_start_relative_position_y = start_boundary_x_and_y[1] - cell_y_position
            cell_end_relative_position_x = end_boundary_x_and_y[0] - cell_x_position
            cell_end_relative_position_y = end_boundary_x_and_y[1] - cell_y_position

            # Resizing coordinates back to the those of the original sized images rounded to whole pixels.
            cell_start_relative_position_x_resized = round(cell_start_relative_position_x / resize_x)
            cell_start_relative_position_y_resized = round(cell_start_relative_position_y / resize_y)
            cell_end_relative_position_x_resized = round(cell_end_relative_position_x / resize_x)
            cell_end_relative_position_y_resized = round(cell_end_relative_position_y / resize_y)


            list_bounding_box_coordinates = [cell_start_relative_position_x_resized, cell_start_relative_position_y_resized,
                                                    cell_end_relative_position_x_resized, cell_end_relative_position_y_resized]

            temporary_list_of_cells_that_have_bounding_boxes.append(bounding_box_start_coordinates_x_y[2])


            # Checks if there is already a key from there already being a bounding box in the cell
            if bounding_box_start_coordinates_x_y[2] in temp_dict_cell_number_and_bounding_boxes:
                temp_dict_cell_number_and_bounding_boxes[bounding_box_start_coordinates_x_y[2]].extend(list_bounding_box_coordinates)

            else:
                temp_dict_cell_number_and_bounding_boxes[bounding_box_start_coordinates_x_y[2]] = list_bounding_box_coordinates

        # Checks if its still within the same cell and if so draws bounding box
        if bounding_box_start_coordinates_x_y[2] == cell_number_on_end_of_drawing and len(cell_numbers_list_for_each_grid) > 0:
            # Check if drawing boundary boxes in span of images that has been selected.
            if bounding_box_start_coordinates_x_y[2] in range(cell_numbers_list_for_each_grid[-2], cell_numbers_list_for_each_grid[-1]+1):
                draw_boundary_box(x, y, bounding_box_start_coordinates_x_y)


# Check if camera opened successfully.
if not cap.isOpened():
    print("Error opening video stream or file")
    sys.exit()

index = 0

cv2.namedWindow('image_selector_from_video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image_selector_from_video', window_width, window_height)


# Read until video is completed
def image_grid(index, x_offset=0, y_offset=0, i=0):
    cap.set(1, index)
    recalculate_window_stuff()
    # Resetting large image to black each time
    l_img = np.zeros((window_height, window_width, 3), np.uint8)
    cv2.imshow('image_selector_from_video', l_img)
    cv2.waitKey(1)
    index_for_frame_list = index

    while i < number_of_cells:
        global enable_draw_on_grid
        enable_draw_on_grid = False
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:

                #  Resize image
                s_image = cv2.resize(frame, (0, 0), None, resize_x, resize_y)

                # Put small images onto large image
                x_offset = (i % number_of_columns) * int(cell_width)
                y_offset = (i // number_of_columns) * int(cell_height)
                l_img[y_offset:y_offset + s_image.shape[0], x_offset:x_offset + s_image.shape[1]] = s_image

                # Show each small images drawn
                cv2.imshow('image_selector_from_video', l_img)
                cv2.waitKey(1)

                # i for count of images, index keeps track of where you are in frames
                i += 1
                index += 1
                if i == number_of_cells or index == frames_in_video:
                    enable_draw_on_grid = True
                    # Parameters passed to mouse click function
                    param = [l_img, index_for_frame_list]
                    while True:

                        cv2.setMouseCallback('image_selector_from_video', click_event, param)
                        c = cv2.waitKey(1)

                        if c == 27:  # Escape
                            print('Esc pressed to Exit')
                            sys.exit()

                        elif c == 32:  # Space
                            print('Space bar pressed go to next images')

                            # Getting rid of an uneven number of cells in lists
                            if len(cell_numbers_temporary) % 2 == 0:
                                pass
                            else:
                                cell_numbers_temporary.pop()
                            if len(cell_numbers_list_for_each_grid) % 2 == 0:
                                pass
                            else:
                                cell_numbers_list_for_each_grid.pop()

                            # Clears lists for the case of single selected rectangle
                            cell_numbers_temporary.clear()
                            image_list.clear()

                            # Creates a image list from the temporary image lists of each grid of images.
                            def create_permanent_image_list():
                                for images in image_list_temporary:
                                    image_list_to_keep.append(images)

                            create_permanent_image_list()

                            # Transforms cell number in temporary grid into frame and appends to frame numbers list
                            def each_grid_cells_into_frames_list():
                                for cell in cell_numbers_list_for_each_grid:
                                    frame_number = int(param[1]) + int(cell)
                                    frame_numbers_list.append(frame_number)

                            each_grid_cells_into_frames_list()



                            # Calculates frames spans backwards and forwards
                            def make_list_of_frames_to_keep(image_count=0):
                                # Putting into a list of two's for calculating frame spans
                                frame_numbers_list_sliced = zip(frame_numbers_list[0::2], frame_numbers_list[1::2])
                                # Clear lists when space pressed
                                list_of_frames_to_keep.clear()
                                image_list_to_print.clear()

                                for numbers in frame_numbers_list_sliced:
                                    # Forward frame spans
                                    if numbers[0] < numbers[1]:
                                        for frames1 in range(numbers[0], numbers[1] + 1):
                                            list_of_frames_to_keep.append(frames1)
                                            image_list_to_print.append(image_list_to_keep[image_count])
                                        image_count += 1

                                    # Backward frame spans
                                    elif numbers[0] > numbers[1]:
                                        for frames2 in range(numbers[1], numbers[0] + 1):
                                            list_of_frames_to_keep.append(frames2)
                                            image_list_to_print.append(image_list_to_keep[image_count])
                                        image_count += 1

                            make_list_of_frames_to_keep()

                            def bounding_box_cell_keys_to_frames():
                                # Changing the key of dict: cell numbers into frame numbers.
                                temp_dict_to_append = {k + int(param[1]): v for (k, v) in temp_dict_cell_number_and_bounding_boxes.items()}
                                perm_dict_cell_number_and_bounding_boxes.update(temp_dict_to_append)
                            bounding_box_cell_keys_to_frames()

                            # Clear temp dict of bounding boxes ready for next lot of frames to have bounding boxes.
                            temp_dict_cell_number_and_bounding_boxes.clear()

                            # Clearing temporary lists, so ready for the next lot of images.
                            cell_numbers_list_for_each_grid.clear()
                            image_list_temporary.clear()

                            def create_text_file():
                                # Creating text file with frame numbers and what user tags images as.
                                file = open('List_of_images.txt', 'w')

                                for i, frame in enumerate(list_of_frames_to_keep):
                                    if frame in perm_dict_cell_number_and_bounding_boxes.keys():
                                        file.write(f'{frame} {image_list_to_print[i]} {perm_dict_cell_number_and_bounding_boxes[frame]} \n')
                                    else:
                                        file.write(f'{frame} {image_list_to_print[i]} \n')

                                file.close()

                            # Output text file on each press of Space.
                            create_text_file()

                            # Continue calling function if hasn't hit end of video
                            if frames_in_video != index:
                                return image_grid(index)

                            # If Space bar pressed and end of the video exit out of loop and save tagging.
                            elif frames_in_video == index:
                                create_text_file()
                                return


# Calls function with index of 0.
image_grid(index)

# When everything done, release the video capture object.
cap.release()

# Closes all the windows.
cv2.destroyAllWindows()

# Shuts program down.
sys.exit()
