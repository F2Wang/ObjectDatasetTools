import numpy as np
import cv2
import glob
from copy import deepcopy
from random import randint
import csv

allinfo = []
allinfo.append(["Filename","Annotation tag","Upper left corner X","Upper left corner Y","Lower right corner X","Lower right corner Y","Occluded"])
writer = csv.writer(open("annotations.csv", "w"), delimiter=";")
folders = glob.glob("LINEMOD/*/")
print(folders)
for folder in folders:
    classlabel = folder[:-1]
    len_dataset = len(glob.glob1(folder+"JPEGImages","*.jpg"))
    for id in range(len_dataset):
        try:
            data = []
            imagepath = folder+"JPEGImages/" + str(id) + ".jpg"
            data.append(imagepath)
            data.append(classlabel)
            img_original = cv2.imread(imagepath)
            mask_dir = folder + "mask/" + str(id) + ".png"
            mask = cv2.imread(mask_dir,0)
            thresh = cv2.threshold(mask.copy(), 30, 255, cv2.THRESH_BINARY)[1]

            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnt = max(contours, key=cv2.contourArea)
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(img_original,(x,y),(x+w,y+h),(0,255,0),2)
            data.append(str(x))
            data.append(str(y))
            data.append(str(x+w))
            data.append(str(y+h))
            data.append(str(0))
            allinfo.append(data)
        
            cv2.imshow("window",img_original)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            pass

writer.writerows(allinfo)
