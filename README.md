## Pills detector
Program is used for detecting and counting specified pills and detecting unidentified objects in real time. In this case it is a representation of a production line.
### Program step by step
![diagram drawio](https://github.com/Venomzky/pills_detector_opencv/assets/139345952/7407b9e7-e7a5-490d-a0f9-c374f21515cf)
### 1.Image segmentation
Frame from a video is converted to grayscale in order to use otsu tresholding on it. Before that gaussian blur is used to make a background more uniform and for better segmentation of pill's edges.

![img](https://github.com/Venomzky/pills_detector_opencv/assets/139345952/42e3ff49-101d-46be-bfd9-77d5fd701310)

### 2.Labeling

![label](https://github.com/Venomzky/pills_detector_opencv/assets/139345952/a8a1f304-a0a3-456d-bf17-113c61ce03b8)

Connected components return x,y coordinates of the component, Using two lists of those coordinates (from current frame and last frame) program analise only the first appearance of an object in the video (In the center of a frame).

### 3.Calcualting parameters
![params](https://github.com/Venomzky/pills_detector_opencv/assets/139345952/08e2d415-a016-4a77-81c2-da7cd7ef55de)

Parameters the program use to classify objects are: area to circle area ratio, contour_length to radius ratio, area, and rbg values.
Program only calculate contour for first appearance of an object.

### 4.Classification
Program uses parameters from file generated using an almost identical program used to generate a file with parameters from test film.
Every known object will be counted and indicated by blue bounding box. Every unknow object will be counted and indicated by red bounding box.

### Program in action

https://github.com/Venomzky/pills_detector_opencv/assets/139345952/768c7b1e-8537-480f-8473-261731a627ae

(foreign object in this case is small round pill)
### Thoughts
Accuracy of program (using video with 86 pills):
Green pills 100%
White long pills 100%
White round pills 93,7%

First thing to improve accuracy would be to use video from source, not mp4 video, because quality of each frame is low. Quality of each frame highly effect parameters, thus effecting model performance. For example area of white round pill in in range 2600-6300 which is huge difference. Next thing would be to reduce recording angle between camera and pills (pills more in the center in y axis or camera set higher). Postion has a significant impact on the fact that the same pill has significantly different parameters depending on position relative to the y-axis. Finally implemented more sophisticated method of classification 
