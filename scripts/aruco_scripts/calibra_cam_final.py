#importa bibliotecas necessarias
import imutils
import os
import numpy
import cv2
from cv2 import aruco
import glob
import yaml
from yaml import dump

##----------------------------------------------------------------------------------------------------------##
##                                              Taken from:                                                                ##
## https://github.com/kyle-bersani/opencv-examples/blob/master/CalibrationByCharucoBoard/CalibrateCamera.py ##
##                                                                                                          ##
##----------------------------------------------------------------------------------------------------------##
## Modificado para o caso em concreto

# macros dos parametros da charuco board
NR_LINHAS_CHARUCO = 5
NR_COLUNAS_CHARUCO = 8 
ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_5X5_50)
TAMANHO_QUADRADOS_M = 0.023
TAMANHO_MARCADORES_M = 0.018

#define e cria uma classe charuco board
#com o nr de linhas e colunas usadas
#bem como  tamanho dos marcadores e quadrados da chessboard
# #cv2.aruco.CharucoBoard.create(squaresX, squaresY, squareLength, markerLength, dictionary) ->retval
CHARUCO_BOARD = aruco.CharucoBoard_create(squaresX=NR_COLUNAS_CHARUCO,squaresY=NR_LINHAS_CHARUCO,squareLength=TAMANHO_QUADRADOS_M,markerLength=TAMANHO_MARCADORES_M,dictionary=ARUCO_DICT)

# cria lista dos parametros a retirar das imagens
corners_charuco = [] # cantos interiores
ids_charuco = [] # ids dos arucos
image_size = None


#imagens da calibração numa pasta, numeradas
images = glob.glob("C:\\Users\\pedro\Python\\pics_calibraçao_fora_auga\\*+.jpg")

# para cada imagem
for iname in images:

    img = cv2.imread(iname)

    # passa a preto e branco
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # deteta marcadores
    corners, ids, _ = aruco.detectMarkers(image=gray,dictionary=ARUCO_DICT)

    # desenha aqueles que foram detetados
    img = aruco.drawDetectedMarkers(image=img, corners=corners)

    # obtem cantos interiores e ids da charuco board
    nr_cantos_int, charuco_corners, charuco_ids = aruco.interpolateCornersCharuco(
            markerCorners=corners,
            markerIds=ids,
            image=gray,
            board=CHARUCO_BOARD)

    #para debug
    print("nr_cantos_int= ", nr_cantos_int)

    #nr_cantos_int= nr de cantos interiores dos chessboard squares
    #apenas fazemos a calibração se mais de 25 cantos forem encontrados
    #de um total de 28
    if nr_cantos_int > 25:
        
        corners_charuco.append(charuco_corners)
        ids_charuco.append(charuco_ids)
        
        # mostra cantos encontrados (para debug)
        img = aruco.drawDetectedCornersCharuco(
                image=img,
                charucoCorners=charuco_corners,
                charucoIds=charuco_ids)
       
        # se nao sabemos tamanho da imagem, definimo-la
        if not image_size:
            image_size = gray.shape[::-1]
    
        # redimensiona a imagem
        proportion = max(img.shape) / 1000.0
        img = cv2.resize(img, (int(img.shape[1]/proportion), int(img.shape[0]/proportion)))

        #mostra output
        cv2.imshow('Charuco board', img)
        cv2.waitKey(0)
        print("[OK]DONE WITH IMAGE: {}".format(iname))
    else:
        print("charuco board nao detetado na imagem: {}".format(iname))

# fecha janela
cv2.destroyAllWindows()

#processamento de imagens completo
#fazer calibracao
#obtem parametros da camara atraves dos cantos interiores da board charuco
calibration, cameraMatrix, distCoeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
        charucoCorners=corners_charuco, #vector of detected charuco corners per frame
        charucoIds=ids_charuco,         #list of identifiers for each corner in charucoCorners per frame
        board=CHARUCO_BOARD,            #Marker Board layout
        imageSize=image_size,           #input image size
        cameraMatrix=None,              #Output 3x3 floating-point camera matrix
        distCoeffs=None)                #Output vector of distortion coefficients
    

print("error={}".format(calibration))
# guarda matriz da camara e coeficientes de distorcao num ficheiro yaml
rawdata = {"camera_matrix": cameraMatrix, "dist_coeff": distCoeffs, "rvecs": rvecs, "tvecs": tvecs}
rawfname = "raw_coeffs_rov.yaml"
with open(rawfname, "w") as f:
    yaml.dump(rawdata, f)

#transforma num ficheiro mais "visualizavel" para humanos
cameraMatrix = cameraMatrix.tolist()
distCoeffs = distCoeffs.tolist()
data = {"camera_matrix": cameraMatrix, "dist_coeff": distCoeffs}
fname = "readable_coeffs_rov.yaml"
with open(fname, "w") as f:
    yaml.dump(data, f)

#fim
print('calibracao feita')



