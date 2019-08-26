
"""
record.py
---------------

Main Function for recording a video sequence into cad (color-aligned-to-depth) 
images and depth images

This code is compatible with legacy camera models supported on librealsense SDK v1
and use 3rd party python wrapper https://github.com/toinsson/pyrealsense

For the newer D series cameras, please use record2.py


"""

# record for 30s after a 5s count down
# or exit the recording earlier by pressing q

RECORD_LENGTH = 30

import png
import json
import logging
logging.basicConfig(level=logging.INFO)
import numpy as np
import cv2
import pyrealsense as pyrs
import time
import os
import sys

def make_directories(folder):
    if not os.path.exists(folder+"JPEGImages/"):
        os.makedirs(folder+"JPEGImages/")
    if not os.path.exists(folder+"depth/"):
        os.makedirs(folder+"depth/")

def print_usage():
    
    print("Usage: record.py <foldername>")
    print("foldername: path where the recorded data should be stored at")
    print("e.g., record.py LINEMOD/mug")
    

if __name__ == "__main__":
    try:
        folder = sys.argv[1]+"/"
    except:
        print_usage()
        exit()

    make_directories(folder)
    # save_color_intrinsics(folder)
    FileName=0
    
    with pyrs.Service() as serv:
        with serv.Device() as dev:
            # Save color intrinsics to the corresponding folder
            intr = dev.__getattribute__('color_intrinsics')
            camera_parameters = {'fx': intr.fx, 'fy': intr.fy,
                                 'ppx': intr.ppx, 'ppy': intr.ppy,
                                 'height': intr.height, 'width': intr.width,
                                 'depth_scale':dev.depth_scale}
    
            with open(folder+'intrinsics.json', 'w') as fp:
                json.dump(camera_parameters, fp)

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
                c = dev.color
                c = cv2.cvtColor(c, cv2.COLOR_RGB2BGR)
                d = dev.dac

                
                # Visualize count down
           
                if time.time() -T_start > 5:
                    filecad= folder+"JPEGImages/%s.jpg" % FileName
                    filedepth= folder+"depth/%s.png" % FileName
                    cv2.imwrite(filecad,c)
                    with open(filedepth, 'wb') as f:
                        writer = png.Writer(width=d.shape[1], height=d.shape[0],
                                            bitdepth=16, greyscale=True)
                        zgray2list = d.tolist()
                        writer.write(f, zgray2list)

                    FileName+=1
                    
                if time.time() -T_start > RECORD_LENGTH + 5:
                    dev.stop()
                    serv.stop()
                    break

                if time.time() -T_start < 5:
                    cv2.putText(c,str(5-int(time.time() -T_start)),(240,320), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 4,(0,0,255),2,cv2.LINE_AA)
                if time.time() -T_start > RECORD_LENGTH:
                    cv2.putText(c,str(RECORD_LENGTH+5-int(time.time()-T_start)),(240,320), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 4,(0,0,255),2,cv2.LINE_AA)
                cv2.imshow('COLOR FRAME',c)
                
           
                    
                # press q to quit the program
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    dev.stop()
                    serv.stop()
                    break

    # Release everything if job is finished
    cv2.destroyAllWindows()
