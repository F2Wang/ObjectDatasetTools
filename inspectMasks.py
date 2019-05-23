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
    
    print "Usage: inspectMasks.py <path>"
    print "path: all or path to the folder"
    print "e.g., inspectMasks.py all, inspectMasks.py LINEMOD/cube"

    
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
        cv2.imshow("Masked", img)
        k = 0xFF & cv2.waitKey(1)


if __name__ == "__main__":
  
    # try:
    if sys.argv[1] == "all":
        folders = glob.glob("LINEMOD/*/")
    elif sys.argv[1]+"/" in glob.glob("LINEMOD/*/"):
        folders = [sys.argv[1]+"/"]
    else:
        print_usage()
        exit()
# except:
#         print_usage()
#         exit()

    for path in folders:
        print path
        visualize(path)
