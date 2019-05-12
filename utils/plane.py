"""
plane.py
---------------

Functions related to plane segmentation.

"""
import numpy as np
import cv2
import cv2.aruco as aruco
from scipy.optimize import leastsq

def f_min(X,p):
    plane_xyz = p[0:3]
    distance = (plane_xyz*X.T).sum(axis=1) + p[3]
    return distance / np.linalg.norm(plane_xyz)

def residuals(params, signal, X):
    return f_min(X, params)

def findplane(cad,d):
    p0 = [0.506645455682, -0.185724560275, -1.43998120646, 1.37626378129]
    sol = None
    gray = cv2.cvtColor(cad, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    #lists of ids and the corners beloning to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    XYZ = [[],[],[]]
    if np.all(ids != None):
        for index,cornerset in enumerate(corners):
            cornerset = cornerset[0]
            for corner in cornerset:
                if d[int(corner[1])][int(corner[0])][2]!= 0:
                    XYZ[0].append(d[int(corner[1])][int(corner[0])][0])
                    XYZ[1].append(d[int(corner[1])][int(corner[0])][1])
                    XYZ[2].append(d[int(corner[1])][int(corner[0])][2])


        XYZ = np.asarray(XYZ)
        sol = leastsq(residuals, p0, args=(None, XYZ))[0]

    return sol

def fitplane(p0,points):
  
    XYZ = np.asarray(points.T)
    sol = leastsq(residuals, p0, args=(None, XYZ))[0]

    return sol

def point_to_plane(X,p):
    height,width,dim = X.shape
    X = np.reshape(X,(height*width,dim))
    plane_xyz = p[0:3]
    distance = (plane_xyz*X).sum(axis=1) + p[3]
    distance = distance / np.linalg.norm(plane_xyz)
    distance = np.reshape(distance,(height,width))
    return distance
