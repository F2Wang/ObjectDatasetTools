"""
DataAcquisitionParameters.py
---------------

Define a set of parameters related to color and depth image acquisition

"""
# Camera serial number

SERIAL = '616203001426'
# Depth camera intrinsic 

camera_intrinsics = {'616203001426': {'fx': 473.5945129394531, 'fy': 473.5945129394531, 'height': 480, 'width': 640, 'coeffs': [0.14428648352622986, 0.022509299218654633, 0.0050826361402869225, 0.0029110093601047993, 0.14566537737846375], 'ppy': 245.69300842285156, 'ppx': 314.96026611328125, 'model': 2}}

# Cut off depth reading greater than DEPTH_THRESH in meter 
DEPTH_THRESH = 0.5 
