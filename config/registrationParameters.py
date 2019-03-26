'''
===============================================================================
Define a set of parameters related to fragment registration
===============================================================================
'''
# Voxel size used to down sample the raw pointcloud for faster ICP
VOXEL_SIZE = 0.001


# Set up parameters for post-processing
# Voxel size for the complete mesh
VOXEL_R = 0.0002

# search for up to N frames for registration, odometry only N=1, all frames N = np.inf
# for any N!= np.inf, the refinement is local
K_NEIGHBORS = 10

# Specify an icp algorithm
# "colored-icp", as in Park, Q.-Y. Zhou, and V. Koltun, Colored Point Cloud Registration Revisited, ICCV, 2017 (slower)
# "point-to-plane", a coarse to fine implementation of point-to-plane icp (faster)

ICP_METHOD = "point-to-plane"

# specify the frenquency of labeling ground truth pose

LABEL_INTERVAL = 1

# specify the frenquency of segments used in mesh reconstruction

RECONSTRUCTION_INTERVAL = 10

