# LINEMOD toolkits

## Introduction

This repository contains tools to create object masks, bounding box labels and 3D reconstructed object mesh (.ply) for object sequences filmed with an RGB-D camera. This project can prepare training and testing data for various deep learning projects such as 6D object pose estimation projects singleshotpose, and many object detection (e.g., faster rcnn) and instance segmentation (e.g., mask rcnn) projects. Ideally, if you have realsense cameras and have some experience with MeshLab or Blender, creating your customized dataset should be as easy as executing a few command line arguments.

This codes in this repository implement a raw 3D model acquisition pipeline through aruco markers and ICP registration. The raw 3D model obtained needs to be processed and noise-removed in a mesh processing software. After this step, there are functions to generate required labels in automatically. 

The codes are currently written for a single object of interest per frame. They can be modified to create a dataset that has several items within a frame.

### License

This code is released under the MIT License (refer to the LICENSE file for details).


## Installation

The installation has been tested on a fresh install of Ubuntu 16.04 with Python 2.7

#### Step 1:

Upgrading any pre-install packages

```bash
sudo apt-get update
sudo apt-get upgrade
```
#### Step 2:

Install pip, a Python package manager, and update

```bash
sudo apt install python-pip
sudo -H pip2 install --upgrade pip
```
#### Step 3:

Install the required packages through apt-get

```bash
sudo apt-get install build-essential cmake git pkg-config libssl-dev
```

#### Step 4:

Install the required packages through pip

```bash
sudo pip install numpy Cython==0.19 pypng scipy scikit-learn open3d-python scikit-image open3d-python tqdm pykdtree opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10  trimesh==2.3.12
```
Note: the code was written for opencv ver > 3.0.0 and ver < 3.4.3, so the code should work out of the box if you install opencv anew as instructed. However, if you have already installed opencv, the code
may need adjustment since different versions of opencv have slightly different API

#### Step 5 (Optional):

Install librealsense and pyrealsense wrapper (if you are using realsense camera F200, SR300)

Note: If you do not need to use python wrapper for the driver, please install the latest SDK which is easy to install, the python wrapper only supports the legacy version, which is not supported anymore, and its installation manual is wrong.

(IMPORTANT): Check your kernel version and make sure you have 4.4 by running:

```bash
uname -r
```

If you install 16.04 recently, your kernel version is most likely higher than 4.4, (e.g., 4.8, 4.10, 4.15). In this case, you do not necessarily need to downgrade your kernel version as 4.4 is still supported on 16.04.

If you do not know how to boot into the 4.4 kernel, you need to access grub and boot into 4.4 using the following step:

```bash
sudo apt-get install linux-image-generic
sudo nano /etc/default/grub && sudo update-grub
```

Comment out GRUB_HIDDEN_TIMEOUT and GRUB_TIMEOUT=0, write the file Ctrl+o and exit Ctrl+x, update-grub will then run. After update-grub, the grub menu should not be hidden when rebooting.

Reboot your computer, go to advanced options, and boot the version starting with 4.4.

Note: make sure you boot with this kernel version when you install the driver and use the camera in the future.

Install librealsense

```bash
git clone https://github.com/IntelRealSense/librealsense
git checkout v1.12.1
```

Make sure that the depth camera is unplugged, and follow the installation steps in
(https://github.com/IntelRealSense/librealsense/blob/v1.12.1/doc/installation.md)

#### NOTE

When you run ./scripts/patch-uvcvideo-16.04.simple.sh, you will get this error: /bin/bash: ./scripts/ubuntu-retpoline-extract-one: No such file or directory

There is no precaution for this, and you need to wait until this error appears to fix this by:

```bash
cd ubuntu-xenial
cp debian/scripts/retpoline-extract-one scripts/ubuntu-retpoline-extract-one
```

And then rerun ./scripts/patch-uvcvideo-16.04.simple.sh (press y when ask if re-apply patch again)

You will also get other errors if you didn’t follow the preparation step. After the errors have been fixed, resume with the remaining steps provided by librealsense.

Install pyrealsense driver

```bash
git clone https://github.com/toinsson/pyrealsense
cd pyrealsense
sudo python setup.py install
```

## Create dataset on customized items

### 1. Preparation

Color print the pdf with the correctly sized aruco markers in the arucomarkers folder. Affix the markers surrounding the object of interest as shown in the picture.

![BackFlow](doc/setup.png)

### 2. Record an object sequence

#### Option 1: Record with a realsense camera

Script is provided to record an object video sequence using a compatible realsense camera. You can run:

```python
python record.py LINEMOD/OBJECTNAME
```
e.g.,

```python
python record.py LINEMOD/sugar
```

to record a sequence of a sugar box. By default the script records for 40 seconds after a countdown of 5. You can change the recording interval or exit the recording by pressing "q". Please steadily move the camera to get different views of the object while maintaining that 2-3 markers are within the field of view of the camera at any time. 

Note that the project assumes all sequences are saved under the folder named "LINEMOD", use other folder names will cause an error to occur. 

If you use record.py to create your sequence, color images, depth aligned to color images, and camera parameters will be automatically saved under the directory of the sequence. 

#### Option 2: Use existing sequence or record with other cameras

If you are using other cameras, please put color images in a folder named "JPEGImages" and the aligned depth images as numpy arrays in a folder named "depth". Name your color images in a sequential order from 0.jpg, 1.jpg ... 600.jpg and your depth images 0.npy ... 600.npy  you should also create a file intrinsics.json under the sequence directory and manually input the camera parameters in the format like below:

{"fx": 614.4744262695312, "fy": 614.4745483398438, "height": 480, "width": 640, "ppy": 233.29214477539062, "ppx": 308.8282470703125, "ID": "620201000292"}

If you don't know your camera's intrinsic, you can put a rough estimate in. All parameters required are fx, fy, cx, cy, where commonly fx = fy and equals to the width of the image and cx and cy is the center of the image. For example, for a 640 x 480 resolution image, fx, fy = 480, cx = 320, cy = 240. 

An example sequence can be downloaded, create a directory named "LINEMOD", extract the example sequence, and put the extracted folder (timer) in LINEMOD. (https://drive.google.com/file/d/1qvKRW-jDPHSaJKkzttfXIoESN0O6Fksr/view?usp=sharing)

### 3. Obtain frame transforms

Compute transforms for frames at the specified interval (interval can be changed in config/registrationParameters) against the first frame, save the transforms(4*4 homogenous transforms) as an numpy array (.npy).

```python
python compute_gt_poses.py LINEMOD/sugar
```

### 4. Register all frames and create mesh for the registered scene.

```python
python register_scene.py LINEMOD/sugar
```
A raw registeredScene.ply will be saved under the specified directory (e.g., LINEMOD/sugar). The registeredScene.ply is a reconstruction of the scene that includes the table top, markers, and any other objects exposed during the scanning, with some level of noise removal. The generated mesh looks something like this:

![BackFlow](doc/unsegmented.png)

Alternatively, if you want to save some effort removing all the unwanted background, you can try creating the mesh with register_segmented instead of register_scene.

```python
python register_segmented.py LINEMOD/sugar
```

Register_segmented should be able to automatically removes all the unwanted background. However, this script currently uses some ad hoc methods for segmenting the background, therefore you may need to tune some parameters for it to work with your object. The most important knob to tune is "MAX_RADIUS", which cuts off any depth reading whose euclidean distance to the center of the aruco markers observed is longer than the value specified. This value is currently set at 0.2 m , if you have a larger object, you may need to increase this value to not cut off parts of your object. Result from running register_segmented looks something like this:

![BackFlow](doc/segmented.png)

### 5. Process the mesh manually

The mesh needs to be processed to 1) remove background that is not of interest. 2) complete the missing side and perform surface reconstruction

An video instruction is posted in [here] (https://youtu.be/BPX-j9xE2EQ)

If you are creating the mesh as a by product to obtain image masks, or use it for projects like singleshotpose. Only the exact mesh geometry is needed while the appearance is not useful. It's therefore acceptable to "close holes" as shown in the video for planar areas. Also, for symmetrical objects, complete the shape manually by symmetry. If you need the exact texture information for the missing side, you will need to film another sequence exposing the missing side and manually aligh 2 pointclouds. 

Make sure that the processed mesh is free of ANY isolated noise.

### 6. Create image masks and label files

When you have completed step 1-4 for all customized objects, run

```python
python create_label_files.py all
```
or 

```python
python create_label_files.py LINEMOD/sugar
```

This step creates image masks (saved under mask) as well as labels files (saved under labels) which are projections of 3D bounding box of the object onto the 2D images. It also creates new mesh files (e.g., sugar.ply) whose AABBs are centered at the origin and are the same dimensions as the OBB. The mask files can be used for training and testing purposes for a deep learning project (e.g., mask-rcnn) 

### (Optional) Create additional files required by singleshotpose

If you create the mesh file for singleshot pose, you need to open those new mesh files in meshlab and save them again by unchecking the binary format option. Those meshes are used by singleshotpose for evaluation and pose estimation purpose, and singleshotpose cannot read mesh that is binary encoded.

Masks and labels created in step 6 is compatible with singleshotpose. Currently, class labels are assigned in a hacky way (e.g., by the order the folder is grabbed among all sequence folders), if you call create_label for each folder they will be assigned the same label, so please read the printout and change class label manually in create_label_files.py.

In addition, you will need to create train and test images

```python
python makeTrainTestfiles.py
```

and create other required path files

For each of the customized object, create an objectname.data file in the cfg folder

To get the object scale(max vertice distance), you can run

```python
python getmeshscale.py
```

This should be everything you need for creating an customized dataset for singleshotpose, please don't forget to update the camera calibration parameters in singleshotpose as well.

### (Optional) Create bounding box labels for object detection projects

After you complete step 6 (generated image masks). Run:

```python
python get_BBs.py
```
This creates annotations.csv that contains class labels and bounding box information for all images under LINEMOD folder.


If you encounter any problems with the code, want to report bugs, etc. please contact me at faninedinburgh[at]gmail[dot]com.
