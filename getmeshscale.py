import numpy as np
import trimesh
import glob
import os

def distance(point_one, point_two):
    return ((point_one[0] - point_two[0]) ** 2 +
            (point_one[1] - point_two[1]) ** 2 + (point_one[2] - point_two[2]) ** 2) ** 0.5

def max_distance(points):
    return max(distance(p1, p2) for p1, p2 in zip(points, points[1:]))

folders = glob.glob("LINEMOD/*/")
for classlabel,folder in enumerate(folders):
    try:
        print(folder)

        mesh = trimesh.load(folder + folder[8:-1] +".ply")
        vertices = mesh.vertices
        maxD = max_distance(vertices.tolist())
        print("Max vertice distance is: %f m." % maxD)
    except:
        print("Mesh does not exist")
