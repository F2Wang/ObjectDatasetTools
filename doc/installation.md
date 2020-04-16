## Installation

The installation has been tested on a fresh install of Ubuntu 16.04 with Python 2.7

#### Step 1:

Upgrading any pre-install packages

```bash
sudo apt-get update
sudo apt-get upgrade
```
#### Step 2:

(Python2)

Install pip, a Python package manager, and update

```bash
sudo apt install python-pip
sudo -H pip2 install --upgrade pip
```
(Python3)
```bash
sudo apt-get -y install python3-pip
sudo -H pip3 install --upgrade pip
```

#### Step 3:

Install the required packages through apt-get

```bash
sudo apt-get install build-essential cmake git pkg-config libssl-dev libgl1-mesa-glx
```

#### Step 4:

(Python2)

Install the required packages through pip

```bash
sudo pip install numpy Cython==0.19 pypng scipy scikit-learn open3d==0.9.0 scikit-image tqdm pykdtree opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10  trimesh==2.38.24
```
Note: the code was written for opencv ver > 3.0.0 and ver < 3.4.3, so the code should work out of the box if you install opencv anew as instructed. However, if you have already installed opencv, the code
may need adjustment since different versions of opencv have slightly different API

(Python3)
```bash
sudo pip3 install numpy Cython==0.19 pypng scipy scikit-learn open3d==0.9.0 scikit-image tqdm pykdtree opencv-python==3.3.0.10 opencv-contrib-python==3.3.0.10  trimesh==2.38.24
```

#### Step 5:

Install librealsense and its python wrapper.

#### 5.1: For legacy models (R200, F200, SR300, LR200, ZR200)

Install librealsense legacy version v1.12.1 (https://github.com/IntelRealSense/librealsense/tree/v1.12.1),
and 3rd party python wrapper for librealsense v1.x (https://github.com/toinsson/pyrealsense)

First, check your kernel version and make sure you have 4.4 by running:

```bash
uname -r
```

If you install 16.04 recently, your kernel version is most likely higher than 4.4, (e.g., 4.8, 4.10, 4.15). In this case, you do not necessarily need to downgrade your kernel version as 4.4 is still supported on 16.04.

If you do not know how to boot into the 4.4 kernel, you need to access grub and boot into 4.4 using the following step:

```bash
sudo apt-get install linux-image-generic
sudo nano /etc/default/grub && sudo update-grub
```

Comment out GRUB_HIDDEN_TIMEOUT and GRUB_TIMEOUT=0, write the file Ctrl+o and exit Ctrl+x, update-grub will run. After update-grub, the grub menu should not be hidden when rebooting.

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
#### 5.2: For newer models (SR300 and D series)

Install Intel realsense SDK 2.0 (https://github.com/IntelRealSense/librealsense),
and its official python wrapper pyrealsense2

Intel realsense SDK 2.0 can be installed easily with pre-build packages and supports multiple Ubuntu LTS kernels. Please follow the installation guide on their website.

After installing the 2.0 SDK, install its python wrapper by 

```bash
pip install pyrealsense2
```
