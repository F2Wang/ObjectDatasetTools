"""
makeTrainTestfiles.py
---------------

Create directories to train and test images in train.txt
and test.txt
"""




import numpy as np
import cv2
import glob
import os
from config.registrationParameters import *


folders = glob.glob("LINEMOD/*/")
for classlabel,folder in enumerate(folders):
    print folder
    try:
        transforms_file = folder + 'transforms.npy'
        transforms = np.load(transforms_file)
        filetrain = open(folder+"train.txt","w")
        filetest = open(folder+"test.txt","w")
        for i in range(len(transforms)):
            message = "LINEMOD/" + folder[8:-1] + "/JPEGImages/" + str(i*LABEL_INTERVAL) + ".jpg" + "\n" 
            filetrain.write(message)
            filetest.write(message)
        filetrain.close()
        filetest.close()
    except:
        pass
