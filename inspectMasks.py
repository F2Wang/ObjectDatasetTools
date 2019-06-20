"""
inspectMasks.py
---------------

Visualize the generated masks

"""
import glob
import sys
import cv2
import os

def print_usage():
    
    print("Usage: inspectMasks.py <path>")
    print("path: all or path to the folder")
    print("e.g., inspectMasks.py all, inspectMasks.py LINEMOD/cube")

    
def visualize(path):
    resultIDs = []
    
    for file in os.listdir(path +"mask"):
        if file.endswith(".png"):
            resultIDs.append(int(file[:-4]))

    resultIDs.sort()

    for id in resultIDs:
        filename_img = path + 'JPEGImages/%s.jpg' % id
        img = cv2.imread(filename_img)
        filename_result = path + 'mask/%s.png' % id
        overlay = cv2.imread(filename_result)
        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
        labelfile = path + 'labels/%s.txt' % id
        if os.path.exists(labelfile):
            with open(labelfile, 'r') as fp:
                lines = fp.readlines()
                for line in lines:
                    info = line.split()
            info = [float(i) for i in info]
            width, length = img.shape[:2]
            one = (int(info[3]*length),int(info[4]*width))
            two = (int(info[5]*length),int(info[6]*width))
            three = (int(info[7]*length),int(info[8]*width))
            four = (int(info[9]*length),int(info[10]*width))
            five = (int(info[11]*length),int(info[12]*width))
            six = (int(info[13]*length),int(info[14]*width))
            seven = (int(info[15]*length),int(info[16]*width))
            eight =  (int(info[17]*length),int(info[18]*width))

            cv2.line(img,one,two,(255,0,0),3)
            cv2.line(img,one,three,(255,0,0),3)
            cv2.line(img,two,four,(255,0,0),3)
            cv2.line(img,three,four,(255,0,0),3)
            cv2.line(img,one,five,(255,0,0),3)
            cv2.line(img,three,seven,(255,0,0),3)
            cv2.line(img,five,seven,(255,0,0),3)
            cv2.line(img,two,six,(255,0,0),3)
            cv2.line(img,four,eight,(255,0,0),3)
            cv2.line(img,six,eight,(255,0,0),3)
            cv2.line(img,five,six,(255,0,0),3)
            cv2.line(img,seven,eight,(255,0,0),3)
            
            
        
        cv2.imshow("Masked", img)
        k = 0xFF & cv2.waitKey(1)


if __name__ == "__main__":
  
    if sys.argv[1] == "all":
        folders = glob.glob("LINEMOD/*/")
    elif sys.argv[1]+"/" in glob.glob("LINEMOD/*/"):
        folders = [sys.argv[1]+"/"]
    else:
        print_usage()
        exit()

    for path in folders:
        print(path)
        visualize(path)
