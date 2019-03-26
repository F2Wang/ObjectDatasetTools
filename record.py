"""
record.py
---------------

Main Function for recording a video sequence into cad (color-aligned-to-depth) 
images and depth images


"""

import logging
logging.basicConfig(level=logging.INFO)
import numpy as np
import cv2
import pyrealsense as pyrs
import time
import os
import sys
from pyrealsense.constants import rs_option
# from config.DataAcquisitionParameters import DEPTH_THRESH

def make_directories(folder):
    if not os.path.exists(folder+"JPEGImages/"):
        os.makedirs(folder+"JPEGImages/")
    if not os.path.exists(folder+"depth/"):
        os.makedirs(folder+"depth/")

def print_usage():
    
    print "Usage: record.py <foldername>"
    print "foldername: path where the recorded data should be stored at"
    print "e.g., record.py LINEMOD/mug"

if __name__ == "__main__":
    try:
        folder = sys.argv[1]+"/"
    except:
        print_usage()
        exit()

    make_directories(folder)
    
    FileName=0
    
    with pyrs.Service() as serv:
        with serv.Device() as dev:

            # Set frame rate
            cnt = 0
            last = time.time()
            smoothing = 0.9
            fps_smooth = 30
            T_start = time.time()
            while True:
                cnt += 1
                if (cnt % 10) == 0:
                    now = time.time()
                    dt = now - last
                    fps = 10/dt
                    fps_smooth = (fps_smooth * smoothing) + (fps * (1.0-smoothing))
                    last = now

                dev.wait_for_frames()
                c = dev.cad
                c = cv2.cvtColor(c, cv2.COLOR_RGB2BGR)
                d = dev.depth

                # # perform the depth cut off
                # d[d > DEPTH_THRESH/8.0*65535] == np.uint16(0)
                # c[d == 0] = np.array([0,0,0],dtype = np.uint8)

                # Visualize count down
                if time.time() -T_start < 5:
                    cv2.putText(c,str(5-int(time.time() -T_start)),(240,320), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 4,(0,0,255),2,cv2.LINE_AA)
                cv2.imshow('CAD',c)
           
                if time.time() -T_start > 5:
                    filecad= folder+"JPEGImages/%s.jpg" % FileName
                    filedepth= folder+"depth/%s.npy" % FileName
                    cv2.imwrite(filecad,c)
                    np.save(filedepth,d)
                    FileName+=1
                    
                # press q to quit the program
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    # Release everything if job is finished
    cv2.destroyAllWindows()
