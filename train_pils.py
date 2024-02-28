import cv2 
import numpy as np
from matplotlib import pyplot as plt
import math
import time
sciezka_do_filmu = 'train1.mp4'
cap = cv2.VideoCapture(sciezka_do_filmu)
data_for_file = []
pill_name = 'zielona'



if not cap.isOpened():
    print("Błąd otwierania pliku wideo.")
    exit()



def labels_compare(n_labels, labels_stats, centroids, old_n_labels, old_labels_stats, old_centroids, labels):

    labels_set = []
    old_labels_set = []
    for i in range(1,n_labels):
        x1 = int(labels_stats[i, cv2.CC_STAT_LEFT]) 
        if x1>500 or x1<300:
            continue
        y1 = int(labels_stats[i, cv2.CC_STAT_TOP])
        labels_set.append([x1, y1, i]) 
    for i in range(1,old_n_labels):
        x2 = int(old_labels_stats[i, cv2.CC_STAT_LEFT]) 
        if x2>500 or x2<300:
            continue
        y2 = int(old_labels_stats[i, cv2.CC_STAT_TOP])
        old_labels_set.append([x2, y2])

    i = 0
    j = 0
    while i < len(labels_set):
        while j < len(old_labels_set):
            dist_x = abs(labels_set[i][0]-old_labels_set[j][0])
            dist_y = abs(labels_set[i][1]-old_labels_set[j][1])
            if dist_y<20 and dist_x<60:
                # print(labels_set[i][0],old_labels_set[j][0])
                labels_set.remove(labels_set[i])
                old_labels_set.remove(old_labels_set[j])
                i = -1
                j = 0
                break
            j+=1
        j = 0
        i += 1

    for label in labels_set:

        x, y, w, h, area  = stats[label[2]][:5]
        bin_pil = thresholded[y-2:y+h+2, x-2:x+w+2]
        color_pil = frame[y-2:y+h+2, x-2:x+w+2,::]
        contour = cv2.findContours(bin_pil,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        (x_axis,y_axis),radius = cv2.minEnclosingCircle(contour[0][0])
        color_mean = cv2.mean(color_pil[int(y_axis)-10:int(y_axis)+10,int(x_axis)-15:int(x_axis)+10, ::])
        radius = int(radius)
        circle_area = 3.14 * radius**2 
        contour_length = cv2.arcLength(contour[0][0], closed=True)

        x, y, w, h, area = stats[label[2]][:5]
        cv2.rectangle(frame, (x,y),(x+w,y+h), (255,0,0), 2)
        #print(area/circle_area, contour_length/radius, area)
        data_for_file.append([area/circle_area, contour_length/radius, area, color_mean[0], color_mean[1], color_mean[2]])
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
    im =  cv2.GaussianBlur(im, (9,9),0)

    #nalozenie otsu
    _,thresholded = cv2.threshold(im, 0, 220, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #operacja opening (erosion then dilation)
    kernel = np.ones((8,8),np.uint8)
    opening = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)

    
    (n, labels, stats, centroids) = cv2.connectedComponentsWithStats(opening)

    labels_compare(n, stats, centroids, old_frame_n, old_labels_stats, old_centroids, labels)

    old_frame_n = n
    old_labels_stats = stats
    old_centroids = centroids

    cv2.imshow("real", frame)

    if cv2.waitKey(300) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

for data in data_for_file:
    if data[2]<1800:
        data_for_file.remove(data)

for data in data_for_file:
    print(data)

min_roundness = 2
max_roundness = 0
min_area = 10000
max_area = 0
min_contourToLength = 100
max_contourToLength = 0
min_b = 1000
max_b = 0
min_g = 1000
max_g = 0
min_r = 1000
max_r = 0


roundnesses = [sublist[0] for sublist in data_for_file]
min_roundness = min(roundnesses)
max_roundness = max(roundnesses)
ratios = [sublist[1] for sublist in data_for_file]
min_contourToLength = min(ratios)
max_contourToLength = max(ratios)
areas = [sublist[2] for sublist in data_for_file]
min_area = int(min(areas))
max_area = int(max(areas))
bs = [sublist[3] for sublist in data_for_file]
min_b = int(min(bs))
max_b = int(max(bs))
gs = [sublist[4] for sublist in data_for_file]
min_g = int(min(gs))
max_g = int(max(gs))
rs = [sublist[5] for sublist in data_for_file]
min_r = int(min(rs))
max_r = int(max(rs))


with open('data.txt', 'a') as f:
    f.write(f"{min_roundness} {max_roundness} {min_contourToLength} {max_contourToLength} {min_area} {max_area} {min_b} {max_b} {min_g} {max_g} {min_r} {max_r} {pill_name}\n")