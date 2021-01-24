# image-selector-opencv-python

image + annotation + imagination === imagotation.

Speed up image selection, tagging and bounding boxing of relevant images to then use in machine learning models.
```
1. The program reads frames/images from a video resizes the original images down into a grid.
2. Allows the user to select a span of images, place bounding boxes and tag the images with text. 
3. A text file containing the frames tagging and boxes is produced on each press of the space bar.
4. The next frames from the video are fed into the grid on Space bar.
```
Keyboard and mouse shortcuts:
```
Esc = Exit the program.
Left mouse click = Select span of images.
Right mouse click = Select bounding boxes.
Middle mouse click = Undo selection.
Space bar = Go to next set of images and store tagged images + frame numbers in text file.
```

```Example of program in use with image span selected and tagged:```
![Screenshot](https://github.com/LeeWannacott/image-selector-opencv-python/blob/master/Example_of_use.png)

```Text file containing list of tagged images with frame numbers and boundary box coordinates:```
![Screenshot](https://github.com/LeeWannacott/image-selector-opencv-python/blob/master/List_of_tagged_images.png)


