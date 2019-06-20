"""
makeTrainTestfiles.py
---------------
Split the train/test images with a simple 80/20 split
Write the train/test image directories in train.txt and test.txt, 
"""

import numpy as np
import cv2
import glob
import os
from config.registrationParameters import *


folders = glob.glob("LINEMOD/*/")
for classlabel,folder in enumerate(folders):
    print(folder)
    try:
        transforms_file = folder + 'transforms.npy'
        transforms = np.load(transforms_file)
        filetrain = open(folder+"train.txt","w")
        filetest = open(folder+"test.txt","w")
        for i in range(len(transforms)):
            message = "LINEMOD/" + folder[8:-1] + "/JPEGImages/" + str(i*LABEL_INTERVAL) + ".jpg" + "\n"
            # train on every 5th of the image
            if i%5 == 0:
                filetrain.write(message)
            else:
                filetest.write(message)
        filetrain.close()
        filetest.close()
    except:
        pass
