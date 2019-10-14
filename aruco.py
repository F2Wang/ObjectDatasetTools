
"""
aruco.py
---------------

Code to examine if aruco markers can be detected on the recorded sequence
A rectangle will be drawn on markers that are detected

"""

import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import png
import sys

def print_usage():
    
    print("Usage: aruco.py <path>")
    print("path: all or name of the folder")
    print("e.g., aruco.py all, aruco.py.py LINEMOD/Cheezit")
    
    
if __name__ == "__main__":
  
    try:
        if sys.argv[1] == "all":
            folders = glob.glob("LINEMOD/*/")
        elif sys.argv[1]+"/" in glob.glob("LINEMOD/*/"):
            folders = [sys.argv[1]+"/"]
        else:
            print_usage()
            exit()
    except:
        print_usage()
        exit()
        
    for path in folders:
        print(path)
        for Filename in xrange(len(glob.glob1(path+"JPEGImages","*.jpg"))):
            img_file = path + 'JPEGImages/%s.jpg' % (Filename)
            color = cv2.imread(img_file)
            depth_file = path + 'depth/%s.png' % (Filename)
            reader = png.Reader(depth_file)
            pngdata = reader.read()
            depth = np.array(tuple(map(np.uint16, pngdata[2])))
            cad = color.copy()
            cad[depth == 0] = np.array([0,0,0],dtype = np.uint8)
            gray = cv2.cvtColor(cad, cv2.COLOR_BGR2GRAY)
            aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
            parameters = aruco.DetectorParameters_create()

            #lists of ids and the corners beloning to each id
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            font = cv2.FONT_HERSHEY_SIMPLEX 

            if np.all(ids != None):

                aruco.drawDetectedMarkers(cad, corners) #Draw A square around the markers


                ###### DRAW ID #####
                cv2.putText(cad, "Id: " + str(ids), (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)


            # Display the resulting frame
            cv2.imshow('Aruco detection on depth thresholded image',cad)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            



    cv2.destroyAllWindows()
