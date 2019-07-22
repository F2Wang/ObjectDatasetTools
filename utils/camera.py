"""
camera.py
---------------

Functions related to data acquisition with cameras.

"""

import numpy as np

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



def convert_depth_frame_to_pointcloud(depth_image, camera_intrinsics):
        
    """
    Convert the depthmap to a 3D point cloud
    Parameters:
    -----------
    depth_frame : (m,n) uint16
        The depth_frame containing the depth map

    camera_intrinsics : dict 
                The intrinsic values of the depth imager in whose coordinate system the depth_frame is computed
    Return:
    ----------
    pointcloud : (m,n,3) float
        The corresponding pointcloud in meters

    """
    
    # [height, width] = depth_image.shape
    # print(depth_image.shape[0])
    height = depth_image.shape[0]
    width = depth_image.shape[1]


    nx = np.linspace(0, width-1, width)
    ny = np.linspace(0, height-1, height)
    u, v = np.meshgrid(nx, ny)
    x = (u.flatten() - float(camera_intrinsics['ppx']))/float(camera_intrinsics['fx'])
    y = (v.flatten() - float(camera_intrinsics['ppy']))/float(camera_intrinsics['fy'])
    depth_image = depth_image*1.0/65535*8.0
    z = depth_image.flatten()
    x = np.multiply(x,z)
    y = np.multiply(y,z)

    pointcloud = np.dstack((x,y,z)).reshape((depth_image.shape[0],depth_image.shape[1],3))

    return pointcloud

def project_point_to_pixel(point, serialnumber, camera_intrinsics):
    depth_image

    height = 480
    width = 640

    nx = np.linspace(0, width-1, width)
    ny = np.linspace(0, height-1, height)
    u, v = np.meshgrid(nx, ny)
    x = (u.flatten() - camera_intrinsics[serialnumber]['ppx'])/camera_intrinsics[serialnumber]['fx']
    y = (v.flatten() - camera_intrinsics[serialnumber]['ppy'])/camera_intrinsics[serialnumber]['fy']
    z = np.ones(height*width)*point[2]
    x = np.multiply(x,z)
    y = np.multiply(y,z)

    pointcloud = np.dstack((x,y,z)).reshape((depth_image.shape[0],depth_image.shape[1],3))
    dis, index = nearest_neighbour(point, pointcloud)
        

    return index

