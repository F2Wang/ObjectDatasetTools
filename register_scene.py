"""
register_scene.py
---------------
Create registered scene pointcloud with ambient noise removal
The registered pointcloud includes the table top, markers, and some noise
This mesh needs to be processed in a mesh processing tool to remove the artifact

"""
import png
import random
import cv2.aruco as aruco
from open3d import *
import numpy as np
import cv2
import os
import glob
from utils.ply import Ply
from utils.camera import *
from registration import icp, feature_registration, match_ransac, rigid_transform_3D
from tqdm import trange
from pykdtree.kdtree import KDTree
import time
import sys
from config.registrationParameters import *
import json

# Set up parameters for registration
# voxel sizes use to down sample raw pointcloud for fast ICP
voxel_size = VOXEL_SIZE
max_correspondence_distance_coarse = voxel_size * 15
max_correspondence_distance_fine = voxel_size * 1.5

# Set up parameters for post-processing
# Voxel size for the complete mesh
voxel_Radius = VOXEL_R

# Point considered an outlier if more than inlier_Radius away from other points  
inlier_Radius = voxel_Radius * 2.5

# search for up to N frames for registration, odometry only N=1, all frames N = np.inf
N_Neighbours = K_NEIGHBORS


def post_process(originals, voxel_Radius, inlier_Radius):
     """
    Merge segments so that new points will not be add to the merged
    model if within voxel_Radius to the existing points, and keep a vote
    for if the point is issolated outside the radius of inlier_Radius at 
    the timeof the merge

    Parameters
    ----------
    originals : List of open3d.Pointcloud classe
      6D pontcloud of the segments transformed into the world frame
    voxel_Radius : float
      Reject duplicate point if the new point lies within the voxel radius
      of the existing point
    inlier_Radius : float
      Point considered an outlier if more than inlier_Radius away from any 
      other points

    Returns
    ----------
    points : (n,3) float
      The (x,y,z) of the processed and filtered pointcloud
    colors : (n,3) float
      The (r,g,b) color information corresponding to the points
    vote : (n, ) int
      The number of vote (seen duplicate points within the voxel_radius) each 
      processed point has reveived
    """

     for point_id in trange(len(originals)):

          if point_id == 0:
               vote = np.zeros(len(originals[point_id].points))
               points = np.array(originals[point_id].points,dtype = np.float64)
               colors = np.array(originals[point_id].colors,dtype = np.float64)

          else:
       
               points_temp = np.array(originals[point_id].points,dtype = np.float64)
               colors_temp = np.array(originals[point_id].colors,dtype = np.float64)
               
               dist , index = nearest_neighbour(points_temp, points)
               new_points = np.where(dist > voxel_Radius)
               points_temp = points_temp[new_points]
               colors_temp = colors_temp[new_points]
               inliers = np.where(dist < inlier_Radius)
               vote[(index[inliers],)] += 1
               vote = np.concatenate([vote, np.zeros(len(points_temp))])
               points = np.concatenate([points, points_temp])
               colors = np.concatenate([colors, colors_temp])

     return (points,colors,vote) 


def load_pcds(path, downsample = True, interval = 1):

    """
    load pointcloud by path and down samle (if True) based on voxel_size 

    """
    

    global voxel_size, camera_intrinsics 
    pcds= []
    
    for Filename in trange(int(len(glob.glob1(path+"JPEGImages","*.jpg"))/interval)):
        img_file = path + 'JPEGImages/%s.jpg' % (Filename*interval)
        # mask = cv2.imread(img_file, 0)
        
        cad = cv2.imread(img_file)
        cad = cv2.cvtColor(cad, cv2.COLOR_BGR2RGB)
        depth_file = path + 'depth/%s.png' % (Filename*interval)
        reader = png.Reader(depth_file)
        pngdata = reader.read()
        depth = np.array(tuple(map(np.uint16, pngdata[2])))
        mask = depth.copy()
        depth = convert_depth_frame_to_pointcloud(depth, camera_intrinsics)


        source = geometry.PointCloud()
        source.points = utility.Vector3dVector(depth[mask>0])
        source.colors = utility.Vector3dVector(cad[mask>0])

        if downsample == True:
            pcd_down = source.voxel_down_sample(voxel_size = voxel_size)
            pcd_down.estimate_normals(geometry.KDTreeSearchParamHybrid(radius = 0.002 * 2, max_nn = 30))
            pcds.append(pcd_down)
        else:
            pcds.append(source)
    return pcds



def nearest_neighbour(a, b):
    """
    find the nearest neighbours of a in b using KDTree
    Parameters
    ----------
    a : (n, ) numpy.ndarray
    b : (n, ) numpy.ndarray

    Returns
    ----------
    dist : n float
      Euclidian distance of the closest neighbour in b to a
    index : n float
      The index of the closest neighbour in b to a in terms of Euclidian distance
    """
    tree = KDTree(b)
    dist, index = tree.query(a)
    return (dist, index)


def print_usage():
    
    print("Usage: register_scene.py <path>")
    print("path: all or name of the folder")
    print("e.g., register_scene.py all, register_scene.py LINEMOD/Cheezit")
    
    
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
        with open(path+'intrinsics.json', 'r') as f:
             camera_intrinsics = json.load(f)

        Ts = np.load(path + 'transforms.npy')


        print("Merge segments")
        originals = load_pcds(path, downsample = False, interval = RECONSTRUCTION_INTERVAL)     
        for point_id in range(len(originals)):
             originals[point_id].transform(Ts[int(RECONSTRUCTION_INTERVAL/LABEL_INTERVAL)*point_id])

        print("Apply post processing")
        points, colors, vote = post_process(originals, voxel_Radius, inlier_Radius)
        ply = Ply(points[vote>1], colors[vote>1])
        meshfile = path + 'registeredScene.ply'

        ply.write(meshfile)
        print("Mesh saved")

