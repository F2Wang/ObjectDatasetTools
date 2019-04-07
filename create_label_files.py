"""
create_label_files.py
---------------

Create label files in compliant with the LINEMOD style
used in singleshotpose
"""

import numpy as np
from pykdtree.kdtree import KDTree
import trimesh
import cv2
import glob
import os
import sys
from tqdm import trange
from scipy.optimize import minimize
from config.DataAcquisitionParameters import SERIAL,camera_intrinsics
from config.registrationParameters import *

def get_camera_intrinsic():
    global camera_intrinsics

    K = np.zeros((3, 3), dtype='float64')
    K[0, 0], K[0, 2] = camera_intrinsics[SERIAL]['fx'], camera_intrinsics[SERIAL]['ppx']
    K[1, 1], K[1, 2] = camera_intrinsics[SERIAL]['fy'], camera_intrinsics[SERIAL]['ppy']

    K[2, 2] = 1.
    return K

def compute_projection(points_3D,internal_calibration):
    points_3D = points_3D.T
    projections_2d = np.zeros((2, points_3D.shape[1]), dtype='float32')
    camera_projection = (internal_calibration).dot(points_3D)
    projections_2d[0, :] = camera_projection[0, :]/camera_projection[2, :]
    projections_2d[1, :] = camera_projection[1, :]/camera_projection[2, :]
    return projections_2d


def print_usage():
    
    print "Usage: create_label_files.py <path>"
    print "path: all or name of the folder"
    print "e.g., create_label_files.py all, create_label_files.py LINEMOD/Cheezit"
    
    
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

    K = get_camera_intrinsic()
    
    for classlabel,folder in enumerate(folders):
        classlabel = 13
        print folder
        path_label = folder + "labels"
        if not os.path.exists(path_label):
            os.makedirs(path_label)

        path_mask = folder + "mask"
        if not os.path.exists(path_mask):
            os.makedirs(path_mask)


        transforms_file = folder + 'transforms.npy'
        transforms = np.load(transforms_file)
        mesh = trimesh.load(folder + folder[8:-1] +".ply")

        Tform = mesh.apply_obb()
        mesh.export(file_obj = folder + folder[8:-1] +".ply")

        
        

        points = mesh.bounding_box.vertices
        center = mesh.centroid
        min_x = np.min(points[:,0])
        min_y = np.min(points[:,1])
        min_z = np.min(points[:,2])
        max_x = np.max(points[:,0])
        max_y = np.max(points[:,1])
        max_z = np.max(points[:,2])
        points = np.array([[min_x, min_y, min_z], [min_x, min_y, max_z], [min_x, max_y, min_z],
                           [min_x, max_y, max_z], [max_x, min_y, min_z], [max_x, min_y, max_z],
                           [max_x, max_y, min_z], [max_x, max_y, max_z]])

        points_original = np.concatenate((np.array([[center[0],center[1],center[2]]]), points))
        points_original = trimesh.transformations.transform_points(points_original, np.linalg.inv(Tform))
                    
        projections = [[],[]]
        for i in trange(len(transforms)):
            mesh_copy = mesh.copy()
            mesh_copy.apply_transform(np.linalg.inv(Tform))

            img = cv2.imread(folder+"JPEGImages/" + str(i*LABEL_INTERVAL) + ".jpg")
            transform = transforms[i]
            transform = np.linalg.inv(transform)
            transformed = trimesh.transformations.transform_points(points_original, transform)

            
            corners = compute_projection(transformed,K)
            corners = corners.T
            corners[:,0] = corners[:,0]/640
            corners[:,1] = corners[:,1]/480


            mesh_copy.apply_transform(transform)
            sample_points = mesh_copy.vertices
            masks = compute_projection(sample_points,K)
            masks = masks.T


            min_x = np.min(masks[:,0])
            min_y = np.min(masks[:,1])
            max_x = np.max(masks[:,0])
            max_y = np.max(masks[:,1])


            image_mask = np.zeros(img.shape[:2],dtype = np.uint8)
            for pixel in masks:
                cv2.circle(image_mask,(int(pixel[0]),int(pixel[1])), 5, 255, -1)
   
            thresh = cv2.threshold(image_mask, 30, 255, cv2.THRESH_BINARY)[1]
    
            _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnt = max(contours, key=cv2.contourArea)
    
            image_mask = np.zeros(img.shape[:2],dtype = np.uint8)
            cv2.drawContours(image_mask, [cnt], -1, 255, -1)

            mask_path = path_mask+"/"+ str(i*LABEL_INTERVAL)+".png"
            cv2.imwrite(mask_path, image_mask)
                
            
            
            file = open(path_label+"/"+ str(i*LABEL_INTERVAL)+".txt","w")
            message = str(classlabel)[:8] + " "
            file.write(message)
            for pixel in corners:
                for digit in pixel:
                    message = str(digit)[:8]  + " "
                    file.write(message)
            message = str((max_x-min_x)/640.0)[:8]  + " "
            file.write(message) 
            message = str((max_y-min_y)/480.0)[:8]
            file.write(message)
            file.close()

