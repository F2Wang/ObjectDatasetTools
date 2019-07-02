"""
create_label_files.py
---------------

This script produces:

1. Reorient the processed registered_scene mesh in a mesh with an AABB centered at the
   origin and the same dimensions as the OBB, saved under the name foldername.ply
2. Create label files with class labels and projections of 3D BBs in the format
   singleshotpose requires, saved under labels
3. Create pixel-wise masks, saved under mask
4. Save the homogeneous transform of object in regards to the foldername.ply in each 
   frame
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
from config.registrationParameters import *
import json

def get_camera_intrinsic(folder):
    with open(folder+'intrinsics.json', 'r') as f:
        camera_intrinsics = json.load(f)


    K = np.zeros((3, 3), dtype='float64')
    K[0, 0], K[0, 2] = float(camera_intrinsics['fx']), float(camera_intrinsics['ppx'])
    K[1, 1], K[1, 2] = float(camera_intrinsics['fy']), float(camera_intrinsics['ppy'])

    K[2, 2] = 1.
    return (camera_intrinsics, K)

def compute_projection(points_3D,internal_calibration):
    points_3D = points_3D.T
    projections_2d = np.zeros((2, points_3D.shape[1]), dtype='float32')
    camera_projection = (internal_calibration).dot(points_3D)
    projections_2d[0, :] = camera_projection[0, :]/camera_projection[2, :]
    projections_2d[1, :] = camera_projection[1, :]/camera_projection[2, :]
    return projections_2d


def print_usage():
    
    print("Usage: create_label_files.py <path>")
    print("path: all or name of the folder")
    print("e.g., create_label_files.py all, create_label_files.py LINEMOD/Cheezit")
    
    
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

    
    for classlabel,folder in enumerate(folders):
        # print(folder[8:-1], "is assigned class label:", classlabel)
        print("%s is assigned class label %d." % (folder[8:-1],classlabel))
        camera_intrinsics, K = get_camera_intrinsic(folder)
        path_label = folder + "labels"
        if not os.path.exists(path_label):
            os.makedirs(path_label)

        path_mask = folder + "mask"
        if not os.path.exists(path_mask):
            os.makedirs(path_mask)

        path_transforms = folder + "transforms"
        if not os.path.exists(path_transforms):
            os.makedirs(path_transforms)



        transforms_file = folder + 'transforms.npy'
        try:
            transforms = np.load(transforms_file)
        except:
            print("transforms not computed, run compute_gt_poses.py first")
            continue
        
        mesh = trimesh.load(folder + "registeredScene.ply")

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
        points_original = trimesh.transformations.transform_points(points_original,
                                                                   np.linalg.inv(Tform))
                    
        projections = [[],[]]
        
        for i in trange(len(transforms)):
            mesh_copy = mesh.copy()
            img = cv2.imread(folder+"JPEGImages/" + str(i*LABEL_INTERVAL) + ".jpg")
            transform = np.linalg.inv(transforms[i])
            transformed = trimesh.transformations.transform_points(points_original, transform)

            
            corners = compute_projection(transformed,K)
            corners = corners.T
            corners[:,0] = corners[:,0]/int(camera_intrinsics['width'])
            corners[:,1] = corners[:,1]/int(camera_intrinsics['height'])

            T = np.dot(transform, np.linalg.inv(Tform))
            mesh_copy.apply_transform(T)
            filename = path_transforms + "/"+ str(i*LABEL_INTERVAL)+".npy"
            np.save(filename, T)
            
            sample_points = mesh_copy.sample(10000)
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
    
            _, contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)
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
            message = str((max_x-min_x)/float(camera_intrinsics['width']))[:8]  + " "
            file.write(message) 
            message = str((max_y-min_y)/float(camera_intrinsics['height']))[:8]
            file.write(message)
            file.close()

