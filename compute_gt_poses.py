"""
compute_gt_poses.py
---------------

Main Function for registering (aligning) colored point clouds with ICP/aruco marker 
matching as well as pose graph optimizating

"""
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


def marker_registration(source,target, MIN_MATCH_COUNT = 12):
     cad_src, depth_src = source
     cad_des, depth_des = target
 
     gray_src = cv2.cvtColor(cad_src, cv2.COLOR_RGB2GRAY)
     gray_des = cv2.cvtColor(cad_des, cv2.COLOR_RGB2GRAY)
     aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
     parameters = aruco.DetectorParameters_create()
    
     #lists of ids and the corners beloning to each id
     corners_src, _ids_src, rejectedImgPoints = aruco.detectMarkers(gray_src, aruco_dict, parameters=parameters)
     corners_des, _ids_des, rejectedImgPoints = aruco.detectMarkers(gray_des, aruco_dict, parameters=parameters)
     try:
         ids_src = []
         ids_des = []
         for i in range(len(_ids_src)):
              ids_src.append(_ids_src[i][0])
         for i in range(len(_ids_des)):
              ids_des.append(_ids_des[i][0])
     except:
         return None

     
     src_good = []
     dst_good = []
     for i,id in enumerate(ids_des):
          if id in ids_src:
               j = ids_src.index(id)
               for count,corner in enumerate(corners_src[j][0]):
                    feature_3D_src = depth_src[int(corner[1])][int(corner[0])]
                    feature_3D_des = depth_des[int(corners_des[i][0][count][1])][int(corners_des[i][0][count][0])]
                    if feature_3D_src[2]!=0 and feature_3D_des[2]!=0:
                         src_good.append(feature_3D_src)
                         dst_good.append(feature_3D_des)
    
     # get rigid transforms between 2 set of feature points through ransac
     try:
          transform = match_ransac(np.asarray(src_good),np.asarray(dst_good))
          return transform
     except:
          return None




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
  
def full_registration(path,max_correspondence_distance_coarse,
                      max_correspondence_distance_fine):

     global N_Neighbours, LABEL_INTERVAL
     pose_graph = PoseGraph()
     odometry = np.identity(4)
     pose_graph.nodes.append(PoseGraphNode(odometry))
     n_pcds = len(glob.glob1(path+"JPEGImages","*.jpg"))/LABEL_INTERVAL
     pcds = [[] for i in range(n_pcds)]
     for source_id in trange(n_pcds):
          if source_id > 0:
               pcds[source_id-1] = []
          for target_id in range(source_id + 1, min(source_id + N_Neighbours,n_pcds)):
               if not pcds[source_id]:
                    pcds[source_id] = load_pcd(path, source_id, downsample = True)
               if not pcds[target_id]:
                    pcds[target_id] = load_pcd(path, target_id, downsample = True)
               
               # derive pairwise registration through feature matching
               color_src, depth_src  = load_images(path, source_id)
               color_dst, depth_dst  = load_images(path, target_id)
               res = marker_registration((color_src, depth_src),
                                      (color_dst, depth_dst))

               if res is None:
                    # if marker_registration fails, perform pointcloud matching

                    transformation_icp, information_icp = icp(
                         pcds[source_id], pcds[target_id], voxel_size, max_correspondence_distance_coarse,
                         max_correspondence_distance_fine, method = ICP_METHOD)

               else:
                    transformation_icp = res
                    information_icp = get_information_matrix_from_point_clouds(
                         pcds[source_id], pcds[target_id], max_correspondence_distance_fine,
                         transformation_icp)

               if target_id == source_id + 1:
                    # odometry
                    odometry = np.dot(transformation_icp, odometry)
                    pose_graph.nodes.append(PoseGraphNode(np.linalg.inv(odometry)))
                    pose_graph.edges.append(PoseGraphEdge(source_id, target_id,
                                                       transformation_icp, information_icp, uncertain = False))
               else:
                    # loop closure
                    pose_graph.edges.append(PoseGraphEdge(source_id, target_id,
                                                  transformation_icp, information_icp, uncertain = True))

     return pose_graph

def load_images(path, ID):
    
    """
    Load a color and a depth image by path and image ID 

    """
    global camera_intrinsics
    
    img_file = path + 'JPEGImages/%s.jpg' % (ID*LABEL_INTERVAL)
    cad = cv2.imread(img_file)

    depth_file = path + 'depth/%s.npy' % (ID*LABEL_INTERVAL)
    depth = np.load(depth_file)
    pointcloud = convert_depth_frame_to_pointcloud(depth, camera_intrinsics)


    return (cad, pointcloud)


def load_pcds(path, downsample = True, interval = 1):

    """
    load pointcloud by path and down samle (if True) based on voxel_size 

    """
    

    global voxel_size, camera_intrinsics 
    pcds= []
    
    for Filename in xrange(len(glob.glob1(path+"JPEGImages","*.jpg"))/interval):
        img_file = path + 'JPEGImages/%s.jpg' % (Filename*interval)
        # mask = cv2.imread(img_file, 0)
        
        cad = cv2.imread(img_file)
        cad = cv2.cvtColor(cad, cv2.COLOR_BGR2RGB)
        depth_file = path + 'depth/%s.npy' % (Filename*interval)
        depth = np.load(depth_file)
        mask = depth.copy()
        depth = convert_depth_frame_to_pointcloud(depth, camera_intrinsics)


        source = PointCloud()
        source.points = Vector3dVector(depth[mask>0])
        source.colors = Vector3dVector(cad[mask>0])

        if downsample == True:
            pcd_down = voxel_down_sample(source, voxel_size = voxel_size)
            estimate_normals(pcd_down, KDTreeSearchParamHybrid(radius = 0.002 * 2, max_nn = 30))
            pcds.append(pcd_down)
        else:
            pcds.append(source)
    return pcds


def load_pcd(path, Filename, downsample = True, interval = 1):

     """
     load pointcloud by path and down samle (if True) based on voxel_size 
     
     """
    

     global voxel_size, camera_intrinsics 
    
 
     img_file = path + 'JPEGImages/%s.jpg' % (Filename*interval)

     cad = cv2.imread(img_file)
     cad = cv2.cvtColor(cad, cv2.COLOR_BGR2RGB)
     depth_file = path + 'depth/%s.npy' % (Filename*interval)
     depth = np.load(depth_file)
     mask = depth.copy()
     depth = convert_depth_frame_to_pointcloud(depth, camera_intrinsics)


     source = PointCloud()
     source.points = Vector3dVector(depth[mask>0])
     source.colors = Vector3dVector(cad[mask>0])

     if downsample == True:
          source = voxel_down_sample(source, voxel_size = voxel_size)
          estimate_normals(source, KDTreeSearchParamHybrid(radius = 0.002 * 2, max_nn = 30))
       
     return source


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
    
    print "Usage: compute_gt_poses.py <path>"
    print "path: all or name of the folder"
    print "e.g., compute_gt_poses.py all, compute_gt_poses.py.py LINEMOD/Cheezit"
    
    
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
         
    
        print path

        with open(path+'intrinsics.json', 'r') as f:
             camera_intrinsics = json.load(f)

        Ts = []

        print "Full registration ..."
        pose_graph = full_registration(path, max_correspondence_distance_coarse,
                                       max_correspondence_distance_fine)

        print "Optimizing PoseGraph ..."
        option = GlobalOptimizationOption(
                max_correspondence_distance = max_correspondence_distance_fine,
                edge_prune_threshold = 0.25,
                reference_node = 0)
        global_optimization(pose_graph,
                GlobalOptimizationLevenbergMarquardt(),
                GlobalOptimizationConvergenceCriteria(), option)


        print "Merge segments"
        originals = load_pcds(path, downsample = False, interval = RECONSTRUCTION_INTERVAL)

        num_annotations = len(glob.glob1(path+"JPEGImages","*.jpg"))/LABEL_INTERVAL

        for point_id in range(num_annotations):
             Ts.append(pose_graph.nodes[point_id].pose)
     
        for point_id in trange(len(originals)):
             print point_id*(RECONSTRUCTION_INTERVAL/LABEL_INTERVAL)
             originals[point_id].transform(pose_graph.nodes[int(point_id*(RECONSTRUCTION_INTERVAL/LABEL_INTERVAL))].pose)

        print "Apply post processing"
        points, colors, vote = post_process(originals, voxel_Radius, inlier_Radius)
        ply = Ply(points, colors)
        meshfile = path + 'registeredScene.ply'

        ply.write(meshfile)
        Ts = np.array(Ts)
        filename = path + 'transforms.npy'
        np.save(filename, Ts)
        print("Mesh saved")

