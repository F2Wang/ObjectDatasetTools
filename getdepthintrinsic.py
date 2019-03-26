"""
getdepthintrinsic.py
---------------

Print out the camera intrinsics(depth)
(IMPORTANT)update the correct camera intrinsics in config/DataAcquisitionParameters.py

"""

import cv2 as cv
import pyrealsense2 as rs

# Create a pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start pipeline
profile = pipeline.start(config)
counter = 0

while True:
    # Capture frame-by-frame
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    colour_frame = frames.get_color_frame()

    # Intrinsics & Extrinsics
    depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
    print depth_intrin
