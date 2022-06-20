# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import math
#!/usr/bin/env python

import cv2
import gi
import numpy as np

gi.require_version('Gst', '1.0')
from gi.repository import Gst


class Video():
    """BlueRov video capture class constructor

    Attributes:
        port (int): Video UDP port
        video_codec (string): Source h264 parser
        video_decode (string): Transform YUV (12bits) to BGR (24bits)
        video_pipe (object): GStreamer top-level pipeline
        video_sink (object): Gstreamer sink element
        video_sink_conf (string): Sink configuration
        video_source (string): Udp source ip and port
    """

    def __init__(self, port=5600):
        """Summary

        Args:
            port (int, optional): UDP port
        """

        Gst.init(None)

        self.port = port
        self._frame = None

        # [Software component diagram](https://www.ardusub.com/software/components.html)
        # UDP video stream (:5600)
        self.video_source = 'udpsrc port={}'.format(self.port)
        # [Rasp raw image](http://picamera.readthedocs.io/en/release-0.7/recipes2.html#raw-image-capture-yuv-format)
        # Cam -> CSI-2 -> H264 Raw (YUV 4-4-4 (12bits) I420)
        self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        # Python don't have nibble, convert YUV nibbles (4-4-4) to OpenCV standard BGR bytes (8-8-8)
        self.video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        # Create a sink to get data
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=2 drop=true'

        self.video_pipe = None
        self.video_sink = None

        self.run()

    def start_gst(self, config=None):
        """ Start gstreamer pipeline and sink
        Pipeline description list e.g:
            [
                'videotestsrc ! decodebin', \
                '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                '! appsink'
            ]

        Args:
            config (list, optional): Gstreamer pileline description list
        """

        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def gst_to_opencv(sample):
        """Transform byte array into np array

        Args:
            sample (TYPE): Description

        Returns:
            TYPE: Description
        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        """ Get Frame

        Returns:
            iterable: bool and image frame, cap.read() output
        """
        return self._frame

    def frame_available(self):
        """Check if frame is available

        Returns:
            bool: true if frame is available
        """
        return type(self._frame) != type(None)

    def run(self):
        """ Get frame to update _frame
        """

        self.start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])

        self.video_sink.connect('new-sample', self.callback)

    def callback(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self.gst_to_opencv(sample)
        self._frame = new_frame

        return Gst.FlowReturn.OK


if __name__ == '__main__':
    # Create the video object
    # Add port= if is necessary to use a different one
    video = Video()

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
    time.sleep(2.0)
    frame_nr = 0
    # loop over the frames from the video stream
    while True:
        # Wait for the next frame
        if not video.frame_available():
            continue
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 1000 pixels
        frame = video.frame()
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
video.stop()




















