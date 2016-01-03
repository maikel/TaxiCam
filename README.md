# Taxi Camera Project

This project will contain some pyhton sources to control a surveillance/camera
system in a car.

## Features

* after signaling take pictures of customers and encrypt them
* try to get pictures where one can see faces
* have pictures deleted after a certain amount of time

## First Impressions

* everything seems possible with simple python scripts
* look into the OpenCV library for face detection

## Install Locally

 * install pip and virtualenv 
 * create virtual enviroment with "virtualenv 'path-to-venv'"
 * install numpy and opencv globally on your system (see http://ntraft.com/opencv-in-a-virtualenv/)
 * get local packages by: <path-to-venv>/bin/pip install -r requirements.txt 
 * copy the cv files to your virtualenv: into 'path-to-venv'/lib/python2.7/site-packages
 * run program with 'path-to-venv'/bin/python scan_cam.py 
