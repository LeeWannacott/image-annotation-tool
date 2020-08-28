# image-selector-opencv-python
```
This program is designed to speed up preprocessing of image data.
Allowing the user to get to the data science modelling step faster.

1. The program reads frames/images from a video downsizes the original images down into a grid.
2. Allows the user to select a span of images, place bounding boxes and tag the images with text. 
3. A text file containing the frame numbers and tagging is produced on each press of the space bar.
4. The next frames from the video are fed into the grid on Space bar.
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
