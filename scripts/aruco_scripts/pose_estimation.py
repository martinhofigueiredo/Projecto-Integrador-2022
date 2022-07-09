# carrega bibliotecas necessarias
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

#descodifica video do rov
#criando uma pipeline com o gstreamer
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

    #---OBTEM DICONARIO E COEFICIENTES DA CAMARA

    #define dicionaro aruco a ser usado
        # N X N e o nr de bits usado
        #ultimo nr e' a gama de ID's 
        #neste caso ID's de 0 a 49
    ARUCO_DICT = cv2.aruco.DICT_4X4_50
    ARUCO_REAL_SIZE_IN_m = 0.1
    arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT)
    arucoParams = cv2.aruco.DetectorParameters_create()

    #carrega coeficientes da camara
    from yaml.loader import UnsafeLoader ## funciona
    with open('raw_rov_dentro_agua_coeffs.yaml') as f:
        #loaded e do tipo dict, ou seja
        #loaded = {"camera_matrix": cameraMatrix, "dist_coeff": distCoeffs, "rvecs": rvecs, "tvecs": tvecs}
        loaded = yaml.load(f, Loader=UnsafeLoader)

    cameraMatrix = loaded.get("camera_matrix")
    distCoeffs = loaded.get("dist_coeff")

    print("[INFO] COeficientes da camara carregados...")

    # inicia o stream de video
    print("[INFO] starting video stream...")
    video = Video()

    time.sleep(1.0)
    frame_nr = 0
    rvecs, tvecs = None, None
    n = 0
    # iteraçao sobre os frames
    while True:
        # espera pelo prox frame
        if not video.frame_available():
            continue
           
        
        frame = video.frame()
        frame_nr +=1

        #redimensiona frame para
        #facilitar calculo computacinal
        frame = imutils.resize(frame, width=1000)
        
        #passa frame a preto e branco (maior eficencia computacional)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        # deteta arucos
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
  

        # desenha no frame arucos detetados
        frame = aruco.drawDetectedMarkers(frame, corners, borderColor=(0, 0, 255))

        # se pelo menos 1 aruco detetado
        if ids is not None and len(corners) > 0:
            
            # obtem vetores de rotaçao e tranlsação
            rvecs, tvecs, objPoints = aruco.estimatePoseSingleMarkers(corners, ARUCO_REAL_SIZE_IN_m, cameraMatrix, distCoeffs) 

            #para cada par de valores
            for rvec, tvec in zip(rvecs, tvecs):
                print("rvecs, tvecs:{},{}".format(rvecs,tvecs))
                #print("dist:{}".format(np.linalg.norm(tvec)))

                #TO DO: enviar para o ROS
                
                #desenha no frame eixos do marcador
                frame = cv2.drawFrameAxes(frame, cameraMatrix, distCoeffs, rvec, tvec, 1, 1)
        # exibe frame     
        cv2.imshow("Frame", frame)
        key_pressed = cv2.waitKey(1) & 0xFF
        # para parar
        if key_pressed == ord('q'):
            break
# conclusão do programa (fechar tudo)
cv2.destroyAllWindows()
video.stop()
