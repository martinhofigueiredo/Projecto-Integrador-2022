# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import math
import yaml
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

    #---GET DICTIONARY AND CAMERA COEFFICIENTS

    #defines aruco dictionary used (MIGHT NEED TO BE CHANGED)
        # N X N is the number of bits used in length and height
        #the last number is the range of ID´s
        #in this case it can read from ID 0 to 49
    ARUCO_DICT = cv2.aruco.DICT_5X5_50#CHANGE HERE
    ARUCO_REAL_SIZE_IN_m = 0.035#CHANGE HERE
    arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT)
    arucoParams = cv2.aruco.DetectorParameters_create()

    from yaml.loader import UnsafeLoader ## works
    with open('raw_coeffs.yaml') as f:
        #loaded e do tipo dict, ou seja
        #loaded = {"camera_matrix": cameraMatrix, "dist_coeff": distCoeffs, "rvecs": rvecs, "tvecs": tvecs}
        loaded = yaml.load(f, Loader=UnsafeLoader)

    cameraMatrix = loaded.get("camera_matrix")
    distCoeffs = loaded.get("dist_coeff")

    print("[INFO] Camera coefficients loaded...")

    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    # Create the video object
    # Add port= if is necessary to use a different one
    video = Video()


    #src=0 for default laptop webcam
    #src=1 for external webcam
    time.sleep(2.0)
    frame_nr = 0
    rvecs, tvecs = None, None
    n = 0
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
        # grayscale image
        #QueryImg = imutils.resize(QueryImg, width=1000)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        # Detect Aruco markers
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
  

        # Outline all of the markers detected in our image
        frame = aruco.drawDetectedMarkers(frame, corners, borderColor=(0, 0, 255))

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
                print("rvecs, tvecs:{},{}".format(rvecs,tvecs))
                #print("dist:{}".format(np.linalg.norm(tvec)))
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #HOW TO GET X,Y,Z FROM TVECS AND RVECS
                #use cv::drawFrameAxes to get world coordinate system axis for object points
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                #QueryImg = aruco.drawAxis(QueryImg, cameraMatrix, distCoeffs, rvec, tvec, 1)
                frame = cv2.drawFrameAxes(frame, cameraMatrix, distCoeffs, rvec, tvec, 1, 1)
        # Display our image     
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key==ord('q'):
            break
# do a bit of cleanup
cv2.destroyAllWindows()
video.stop()