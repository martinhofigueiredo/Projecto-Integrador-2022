#---IMPORT

from re import T
import cv2
from imutils.video import VideoStream
import imutils
import numpy as np
#--//--
import imutils
import os
#import numpy
import cv2
from cv2 import aruco
##import pickle
import glob
import yaml
from yaml import dump
#--//--
#from asyncio.windows_events import NULL
from cv2 import sqrt
import imutils
import cv2
#import sys
import time
import math
import numpy as np
#--//--
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import math

from yaml.loader import UnsafeLoader ## works
from cv2 import cvtColor

#import pygst
#from pygst import gi
#gi.require_version('Gst', '1.0')
#import gst

print("[INFO] Finished importing...")

#---GET DICTIONARY AND CAMERA COEFFICIENTS

    #defines aruco dictionary used (MIGHT NEED TO BE CHANGED)
        # N X N is the number of bits used in length and height
        #the last number is the range of ID´s
        #in this case it can read from ID 0 to 49
ARUCO_DICT = cv2.aruco.DICT_5X5_50#CHANGE HERE
ARUCO_REAL_SIZE_IN_m = 0.035#CHANGE HERE
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT)
arucoParams = cv2.aruco.DetectorParameters_create()

    #loads camera calibration files
        #cameraMatrix and distCoeffs needed
        #rvecs and tvecs probably not
from yaml.loader import UnsafeLoader ## works
with open('raw_coeffs.yaml') as f:
    #loaded e do tipo dict, ou seja
    #loaded = {"camera_matrix": cameraMatrix, "dist_coeff": distCoeffs, "rvecs": rvecs, "tvecs": tvecs}
    loaded = yaml.load(f, Loader=UnsafeLoader)

cameraMatrix = loaded.get("camera_matrix")
distCoeffs = loaded.get("dist_coeff")

print("[INFO] Camera coefficients loaded...")

#---GET IMAGE/VIDEO STREAM
    #-if image
        #INPUT_IMG ="<PATH NAME>"
        #image = cv2.imread(INPUT_IMG)
#image = imutils.resize(image, width=600)#CHANGE HERE(?)
    #-if video
        #src=0 for default laptop webcam
        #src=1 for external webcam
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()#CHANGE HERE
#vs = cv2.VideoCapture(0)
time.sleep(2.0)#to allow camera sensor to warm up

#DETECT MARKERS
#PROCESS POSITION
#OUTPUT
#frame_nr = 0
    #Create vectors we'll be using for rotations and translations for postures
rvecs, tvecs = None, None
n = 0
t_mean = 0
while(True):
    # Capturing each frame of our video stream
    #timer_end_off = time.time()
    timer_start_duty = time.time()
    QueryImg = vs.read()
    
    # grayscale image
    #QueryImg = imutils.resize(QueryImg, width=1000)
    gray = cv2.cvtColor(QueryImg, cv2.COLOR_BGR2GRAY)
    
    # Detect Aruco markers
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
  

    # Outline all of the markers detected in our image
    QueryImg = aruco.drawDetectedMarkers(QueryImg, corners, borderColor=(0, 0, 255))

    # verify *at least* one ArUco marker was detected
    if ids is not None and len(corners) > 0:
        # Estimate the posture of the gridboard, which is a construction of 3D space based on the 2D video 
        #pose, rvec, tvec = aruco.estimatePoseBoard(corners, ids, board, cameraMatrix, distCoeffs)
        #if pose:
        #    # Draw the camera posture calculated from the gridboard
        #    QueryImg = aruco.drawAxis(QueryImg, cameraMatrix, distCoeffs, rvec, tvec, 0.3)
        # Estimate the posture per each Aruco marker
        rvecs, tvecs, objPoints = aruco.estimatePoseSingleMarkers(corners, ARUCO_REAL_SIZE_IN_m, cameraMatrix, distCoeffs) 
        timer_end_duty = time.time()
        
        #timer_start_off = time.time()
        #print("dist:{}".format(np.linalg.norm(tvecs)))
        for rvec, tvec in zip(rvecs, tvecs):
            #print("rvecs, tvecs:{},{}".format(rvecs,tvecs))
            #print("dist:{}".format(np.linalg.norm(tvec)))
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #HOW TO GET X,Y,Z FROM TVECS AND RVECS
            #use cv::drawFrameAxes to get world coordinate system axis for object points
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #QueryImg = aruco.drawAxis(QueryImg, cameraMatrix, distCoeffs, rvec, tvec, 1)
            QueryImg = cv2.drawFrameAxes(QueryImg, cameraMatrix, distCoeffs, rvec, tvec, 1, 1)
    # Display our image
    cv2.imshow('QueryImage', QueryImg)
    #t_duty = timer_end_duty - timer_start_duty
    n+=1
    #t_mean += t_duty
    
    #print("time in duty:{}".format(t_duty))
    #f_duty = 1 / t_mean
    #print("freq:{} Hz".format(f_duty))
    #print("time in off:{}".format(timer_end_off - timer_start_off))

    # Exit at the end of the video on the 'q' keypress
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#t_mean /= n
#f_duty = 1 / t_mean
#print("avg freq:{} Hz".format(f_duty))
cv2.destroyAllWindows()