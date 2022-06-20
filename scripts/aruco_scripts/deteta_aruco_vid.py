# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import math

ARUCO_DICT = cv2.aruco.DICT_5X5_50
ARUCO_REAL_SIZE_IN_m = 0.035

# load the ArUCo dictionary and grab the ArUCo parameters
print("[INFO] detecting '{}' tags...".format(ARUCO_DICT))
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT)
arucoParams = cv2.aruco.DetectorParameters_create()

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")

#src=0 for default laptop webcam
#src=1 for external webcam
vs = VideoStream(src=1).start()
time.sleep(2.0)
frame_nr = 0
# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    frame = vs.read()
    frame_nr +=1
    frame = imutils.resize(frame, width=1000)
    # detect ArUco markers in the input frame
    timer_start = time.time()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
        arucoDict, parameters=arucoParams)
    timer_end = time.time()
    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:

        #just to print additional info
        #print('[INFO] Time to detect frame %d was: %s' %(frame_nr, (timer_end-timer_start)))
        
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
                        # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                (topLeft[0], topLeft[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)
    # show the output frame

    
    #----------------------------------------------
    
        #calcula distancias geometricas em pixels
        dist_x_cima = int(topRight[0]-topLeft[0])
        dist_y_cima = int(topRight[1]-topLeft[1])

        dist_x_baixo = int(bottomRight[0]-bottomLeft[0])
        dist_y_baixo = int(bottomRight[1]-bottomLeft[1])

        dist_x_esquerda = int(bottomLeft[0]-topLeft[0])
        dist_y_esquerda = int(bottomLeft[1]-topLeft[1])

        dist_x_direita = int(bottomRight[0]-topRight[0])
        dist_y_direita = int(bottomRight[1]-topRight[1])

        pixel_dist_aresta_cima = math.sqrt((pow(dist_x_cima,2)) + (pow(dist_y_cima,2)))
        pixel_dist_aresta_baixo = math.sqrt((pow(dist_x_baixo,2)) + (pow(dist_y_baixo,2)))
        pixel_dist_aresta_esquerda = math.sqrt((pow(dist_x_esquerda,2)) + (pow(dist_y_esquerda,2)))
        pixel_dist_aresta_direita = math.sqrt((pow(dist_x_direita,2)) + (pow(dist_y_direita,2)))

        #distancia focal
        dist_focal_webcam = 1040

        #calcula distancia real
        dist_real_cima = (ARUCO_REAL_SIZE_IN_m*dist_focal_webcam)/pixel_dist_aresta_cima
        dist_real_baixo = (ARUCO_REAL_SIZE_IN_m*dist_focal_webcam)/pixel_dist_aresta_baixo
        dist_real_esquerda = (ARUCO_REAL_SIZE_IN_m*dist_focal_webcam)/pixel_dist_aresta_esquerda
        dist_real_direita = (ARUCO_REAL_SIZE_IN_m*dist_focal_webcam)/pixel_dist_aresta_direita

        #calcula distancia media, passa para cm e passa a int para mostrar no frame
        dist_med = (dist_real_cima+dist_real_baixo+dist_real_esquerda+dist_real_direita)/4
        dist_med *= 100
        dst = int(dist_med)

        #para mostrar no frame
        cv2.putText(frame, str("Distancia:"), (0,60), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
        cv2.putText(frame, str(dst), (0,90), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
        cv2.putText(frame, str("cm"), (60,90), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)
        





    
    #----------------------------------------------
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()




















