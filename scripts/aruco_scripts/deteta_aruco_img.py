# import the necessary packages
#import argparse
#from functools import total_ordering
#from tkinter import Image
#import posix
from asyncio.windows_events import NULL
from cv2 import sqrt
import imutils
import cv2
#import sys
import time
import math
import numpy as np

cameraMatrix = np.ones((3,3))



#defines aruco dictionary used (MIGHT NEED TO BE CHANGED)
# N X N is the number of bits used in length and height
#the last number is the range of ID´s
#in this case it can read from ID 0 to 49
ARUCO_DICT = cv2.aruco.DICT_5X5_50
ARUCO_REAL_SIZE_IN_m = 0.035

INPUT_IMG ="C:\\Users\\pedro\Python\\aruco_imgs\\aruco_a50cm.jpg"

# load the input image from disk and resize it
#resize might need adjustments
print("[INFO] loading image...")
#start_time = time.time()#to analyze time taken
image = cv2.imread(INPUT_IMG)
image = imutils.resize(image, width=600)

# load the ArUCo dictionary, grab the ArUCo parameters, and detect
# the markers
print("[INFO] detecting '{}' tags...".format(ARUCO_DICT))
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT)
arucoParams = cv2.aruco.DetectorParameters_create()


start_time = time.time()#to analyze time taken
#creates a tuple
#corners = (x,y) coordinates of the corners of the marker
#ids = ID's of the marker
#rejected = list of potential markers that were rejected
(corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict, parameters=arucoParams)

end_time = time.time()#to analyze time taken
detection_time = end_time - start_time
# verify *at least* one ArUco marker was detected
if len(corners) > 0:
    # flatten the ArUco IDs list (makes list "1Dimension")
    ids = ids.flatten()
    # loop over the detected ArUCo corners
    for (markerCorner, markerID) in zip(corners, ids):
        # extract the marker corners (which are always returned in
        # top-left, top-right, bottom-right, and bottom-left order)
        corners = markerCorner.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = corners
        # convert each of the (x, y)-coordinate pairs to integers
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))
        # draw the bounding box of the ArUCo detection
        cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
        cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
        cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
        cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
        # compute and draw the center (x, y)-coordinates of the ArUco
        # marker
        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        cY = int((topLeft[1] + bottomRight[1]) / 2.0)
        cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
        # draw the ArUco marker ID on the image
        cv2.putText(image, str(markerID),
             (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
             0.5, (0, 255, 0), 2)
        


        cv2.putText(image, str("ARUCO DETECTION"), (0,30), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)


        #calcula distancias geometricas em pixels
        dist_x_cima = int(topRight[0]-topLeft[0])
        dist_y_cima = int(topRight[1]-topLeft[1])

        dist_x_baixo = int(bottomRight[0]-bottomLeft[0])
        dist_y_baixo = int(bottomRight[1]-bottomLeft[1])

        dist_x_esquerda = int(bottomLeft[0]-topLeft[0])
        dist_y_esquerda = int(bottomLeft[1]-topLeft[1])

        dist_x_direita = int(bottomRight[0]-topRight[0])
        dist_y_direita = int(bottomRight[1]-topRight[1])

        #dist_x_diag02 = int(bottomRight[0]-topLeft[0])
        #dist_y_diag02 = int(bottomRight[1]-topLeft[1])

        #dist_x_diag13 = int(topRight[0]-bottomLeft[0])
        #dist_y_diag13 = int(bottomLeft[1]-topRight[1])

        pixel_dist_aresta_cima = math.sqrt((pow(dist_x_cima,2)) + (pow(dist_y_cima,2)))
        pixel_dist_aresta_baixo = math.sqrt((pow(dist_x_baixo,2)) + (pow(dist_y_baixo,2)))
        pixel_dist_aresta_esquerda = math.sqrt((pow(dist_x_esquerda,2)) + (pow(dist_y_esquerda,2)))
        pixel_dist_aresta_direita = math.sqrt((pow(dist_x_direita,2)) + (pow(dist_y_direita,2)))
        #pixel_dist_aresta_diag02=math.sqrt((pow(dist_x_diag02,2)) + (pow(dist_y_diag02,2)))
        #pixel_dist_aresta_diag13=math.sqrt((pow(dist_x_diag13,2)) + (pow(dist_y_diag13,2)))


        #D_focal = (nr_pixels * Distance2target)/known_width
        dist_focal_smartphone = 641.3084226 #considerando regua 17cm
        #dist_focal_smartphone = 565.8603729  #considerando regua 15cm


        #calcula distancia real
        dist_real_cima = (ARUCO_REAL_SIZE_IN_m*dist_focal_smartphone)/pixel_dist_aresta_cima
        dist_real_baixo = (ARUCO_REAL_SIZE_IN_m*dist_focal_smartphone)/pixel_dist_aresta_baixo
        dist_real_esquerda = (ARUCO_REAL_SIZE_IN_m*dist_focal_smartphone)/pixel_dist_aresta_esquerda
        dist_real_direita = (ARUCO_REAL_SIZE_IN_m*dist_focal_smartphone)/pixel_dist_aresta_direita

        #diagonais precisam ajuste-> width nao e 35mm!!!!
        #dist_real_diag02 = (ARUCO_REAL_SIZE_IN_m*dist_focal_smartphone)/pixel_dist_aresta_diag02
        #dist_real_diag13 = (ARUCO_REAL_SIZE_IN_m*dist_focal_smartphone)/pixel_dist_aresta_diag13

        #calcula distancia media
        dist_med = (dist_real_cima+dist_real_baixo+dist_real_esquerda+dist_real_direita)/4
        dist_med *= 100     #para ficar em cm
        dst = int(dist_med) #para mostrar na imagem apenas valor inteiro

        #para por texto na imagem
        cv2.putText(image, str("Distancia:"), (0,60), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
        cv2.putText(image, str(dst), (0,90), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
        cv2.putText(image, str("cm"), (60,90), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)

        distCoeffs = NULL
        cameraMatrix = 0
        rvec = 0
        tvec = 0 
        objectPoints = 0
        #qeisto = cv2.projectPoints(corners, rvec, tvec, cameraMatrix, distCoeffs)

        print("--------------[INFO] ArUco marker ID:{} ---------------------".format(markerID))
        #print("[INFO] coordinates of {} corner: {}".format("Top Left",topLeft))
        #print("[INFO] coordinates of {} corner: {}".format("Top Right",topRight))
        #print("[INFO] coordinates of {} corner: {}".format("Bottom Left",bottomLeft))
        #print("[INFO] coordinates of {} corner: {}".format("Bottom Right",bottomRight))

        #print("[INFO] dist aresta em pixels cima: %f" %pixel_dist_aresta_cima)
        #print("[INFO] dist aresta em pixels baixo: %f" %pixel_dist_aresta_baixo)
        #print("[INFO] dist aresta em pixels esq: %f" %pixel_dist_aresta_esquerda)
        #print("[INFO] dist aresta em pixels dir: %f" %pixel_dist_aresta_direita)

        print("[INFO] dist real a aruco cima: %f" %dist_real_cima)
        print("[INFO] dist real a aruco baixo: %f" %dist_real_baixo)
        print("[INFO] dist real a aruco esq: %f" %dist_real_esquerda)
        print("[INFO] dist real a aruco dir: %f" %dist_real_direita)

        print("[INFO] DISTANCIA MEDIA: %f cm" %dist_med)
        
        print("[INFO] Detection done in %.9f seconds" % detection_time)
        

# show the output image
cv2.imshow("Image", image)
# save image
#output_img = 'output_0_inclinado.jpg'
#cv2.imwrite(output_img, image)
cv2.waitKey(0)







