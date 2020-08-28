# image-selector-opencv-python
```
This program is designed to speed up preprocessing of image data; so the user can get to the data science modelling step faster.
It helps with image selection and putting bounding boxes on images.

The program reads images from a video and resizes the original images down into a grid. Allows 
the user to select a span of images and tag the images with text. A text file containing the frame numbers and tagging 
is produced on each press of the space bar; The next images fed into the grid on Space bar.
```
Keyboard and mouse shortcuts:
```
Esc = Exit the program.
Left mouse click = Select span of images.
Right mouse click = Undo image span selection.
Space bar = Go to next set of images and store tagged images + frame numbers in text file.
```

```Example of program in use with images selected and entering a tag for image span```
![Screenshot](https://github.com/LeeWannacott/image-selector-opencv-python/blob/master/Example_of_use.png)

```Text file with list of tags and corresponding frame numbers produced on each Space bar```
![Screenshot](https://github.com/LeeWannacott/image-selector-opencv-python/blob/master/List_of_images.png)
