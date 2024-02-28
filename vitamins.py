import cv2 
import numpy as np
from matplotlib import pyplot as plt
import math
import time

video_path = 'acc_test.mp4'
pills_data_path = 'data.txt'

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Błąd otwierania pliku wideo.")
    exit()

class Wrong_object:
    def __init__(self):
        self.counter = 0

wrong_object = Wrong_object()

class Pill:
    def __init__(self, min_roundness, max_roundness, min_contourToLength, max_contourToLength, min_area, max_area, min_b, max_b, min_g, max_g, min_r, max_r,name):
        self.min_roundness = min_roundness
        self.max_roundness = max_roundness
        self.min_contourToLength = min_contourToLength
        self.max_contourToLength = max_contourToLength
        self.min_area = min_area
        self.max_area = max_area
        self.min_b = min_b
        self.max_b = max_b
        self.min_g = min_g
        self.max_g = max_g
        self.min_r = min_r
        self.max_r = max_r
        self.name = name
        self.counter = 0

pills = []
with open(pills_data_path, 'r') as file:
    for line in file:
        values = line.strip().split()        
        min_roundness = float(values[0])
        max_roundness = float(values[1])
        min_contourToLength = float(values[2])
        max_contourToLength = float(values[3])
        min_area = int(values[4])
        max_area = int(values[5])
        min_b = int(values[6])
        max_b = int(values[7])
        min_g = int(values[8])
        max_g = int(values[9])
        min_r = int(values[10])
        max_r = int(values[11])
        name = values[12]
        pill = Pill(min_roundness, max_roundness, min_contourToLength, max_contourToLength,min_area, max_area, min_b, max_b, min_g, max_g, min_r, max_r,name)
        pills.append(pill)

def imshow_components(labels):
    # Map component labels to hue val
    label_hue = np.uint8(179*labels/np.max(labels))
    blank_ch = 255*np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

    # cvt to BGR for display
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

    # set bg label to black
    labeled_img[label_hue==0] = 0

    return labeled_img


def clasify_object(roundness, contourToLength, area, b,g,r):
    roundness_delta = 0.1
    contourToLength_delta = 0.11
    bgr_delta = 15
    area_delta = 300
    for pil in pills:
        if roundness<=pil.max_roundness+roundness_delta and roundness>=pil.min_roundness-roundness_delta and contourToLength<=pil.max_contourToLength+contourToLength_delta and contourToLength >=pil.min_contourToLength-contourToLength_delta and area <= pil.max_area+area_delta and area >= pil.min_area-area_delta and b <= pil.max_b+bgr_delta and b >= pil.min_b-bgr_delta and g <= pil.max_g+bgr_delta and g>= pil.min_g-bgr_delta and r<= pil.max_r+bgr_delta and r>= pil.min_r-bgr_delta:
            pil.counter +=1
            return 0
    return 1 


def compare_frames(n_labels, labels_stats, old_n_labels, old_labels_stats):

    left_border = 300
    right_border = 500

    labels_set = []
    old_labels_set = []
    for i in range(1,n_labels):
        x1 = int(labels_stats[i, cv2.CC_STAT_LEFT]) 
        if x1>right_border or x1<left_border:
            continue
        y1 = int(labels_stats[i, cv2.CC_STAT_TOP])
        labels_set.append([x1, y1, i]) 
    for i in range(1,old_n_labels):
        x2 = int(old_labels_stats[i, cv2.CC_STAT_LEFT]) 
        if x2>right_border or x2<left_border:
            continue
        y2 = int(old_labels_stats[i, cv2.CC_STAT_TOP])
        old_labels_set.append([x2, y2])

    i = 0
    j = 0

    min_pill_distance = 20
    max_pill_distance = 60

    while i < len(labels_set):
        while j < len(old_labels_set):
            dist_x = abs(labels_set[i][0]-old_labels_set[j][0])
            dist_y = abs(labels_set[i][1]-old_labels_set[j][1])
            if dist_y<min_pill_distance and dist_x<max_pill_distance:
                # print(labels_set[i][0],old_labels_set[j][0])
                labels_set.remove(labels_set[i])
                old_labels_set.remove(old_labels_set[j])
                i = -1
                j = 0
                break
            j+=1
        j = 0
        i += 1
    
    return labels_set

def analise_by_contour(labels_set):
    for label in labels_set:

        color_sample_size = 10

        x, y, w, h, area  = stats[label[2]][:5]
        bin_pil = thresholded[y-2:y+h+2, x-2:x+w+2]
        color_pil = frame[y-2:y+h+2, x-2:x+w+2,::]
        contour = cv2.findContours(bin_pil,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        (x_axis,y_axis),radius = cv2.minEnclosingCircle(contour[0][0])
        color_mean = cv2.mean(color_pil[int(y_axis)-color_sample_size:int(y_axis)+color_sample_size,int(x_axis)-color_sample_size:int(x_axis)+color_sample_size, ::])
        radius = int(radius)
        circle_area = 3.14 * radius**2 
        contour_length = cv2.arcLength(contour[0][0], closed=True)
        ret = clasify_object(area/circle_area, contour_length/radius, area, int(color_mean[0]), int(color_mean[1]), int(color_mean[2]))
        if ret:
            cv2.rectangle(frame, (x,y),(x+w,y+h), (0,0,255), 4)
            wrong_object.counter += 1
            print("wrong_object")
            print(area)

        else:
            cv2.rectangle(frame, (x,y),(x+w,y+h), (255,0,0), 2)
        cv2.imshow("real", frame)

    return 0





old_frame_n = 0
old_labels_stats = 0
old_centroids = 0
frame = 0




while True:
    ret, frame = cap.read()
    if not ret:
        break
    #frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #blur dla lepszego odzielenia obiektow od tla
    im =  cv2.GaussianBlur(im, (7,7),0)


    #nalozenie otsu
    _,thresholded = cv2.threshold(im, 0, 220, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #operacja opening (erosion then dilation)
    kernel = np.ones((8,8),np.uint8)
    opening = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)

    
    (n, labels, stats, centroids) = cv2.connectedComponentsWithStats(opening)
    new_labels_set = compare_frames(n, stats, old_frame_n, old_labels_stats )
    analise_by_contour(new_labels_set)
    old_frame_n = n
    old_labels_stats = stats
    #color_img = imshow_components(labels)
    offset = 40
    for pill in pills:
        score = f'{pill.name}: {pill.counter}'
        cv2.putText(frame, score, (0,offset), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255))
        offset +=40
    score = f'unfamiliar: {wrong_object.counter}'
    cv2.putText(frame, score, (0,offset), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255))

    cv2.imshow("real", frame)
    #cv2.imshow("xD", color_img)q
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


for pil in pills:
    print(pil.counter, pil.name)
print(wrong_object.counter, "errors")