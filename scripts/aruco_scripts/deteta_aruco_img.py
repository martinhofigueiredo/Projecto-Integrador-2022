# carrega bibliotecas
from cv2 import sqrt
import imutils
import cv2
#import sys
import time
import math
import numpy as np





#defne dicionario aruco a ser usado
# N X N é o nr de bits usado em cada lado do marcador
#ultimo nr é a gama de ID's
#neste caso de 0 a 49
ARUCO_DICT = cv2.aruco.DICT_4X4_50#dicionario arucos feup
#ARUCO_REAL_SIZE_IN_m = 0.035
ARUCO_REAL_SIZE_IN_m = 0.1#tamanho marcadores no tanque
#INPUT_IMG ="C:\\Users\\pedro\Python\\aruco_imgs\\aruco_a50cm.jpg"
#imagem a analisar
INPUT_IMG ="pics_arucos_agua/20cmlado8.jpg"

output_img = 'output_rov_20cm7.jpg'

# carrega e redimensiona a imagem
print("[INFO] carregado imagem...")
image = cv2.imread(INPUT_IMG)
image = imutils.resize(image, width=600)

# carrega dicionário
print("[INFO] a detetar tags '{}' ".format(ARUCO_DICT))
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT)
arucoParams = cv2.aruco.DetectorParameters_create()


start_time = time.time()#para analizar tempo
#deteta marcadores
#-cria uma tupla
#corners = (x,y) coordenadas em pixeis dos cantos
#ids = ID's do marcador
#rejected = lista de potenciais marcadores
(corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict, parameters=arucoParams)

end_time = time.time()#para analisar tempo
detection_time = end_time - start_time
# verifica que pelo menos 1 aruco foi
#identificado
if len(corners) > 0:
    # passa lista de ids para 1 dimensão
    ids = ids.flatten()
    # para cada canto de cada marcador
    for (markerCorner, markerID) in zip(corners, ids):
        #transforma em lista de listas
        #especie de matriz, com coordenadas dos pixeis
        #de cada canto numa linha
        corners = markerCorner.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = corners
        # converte coordenadas para inteiros
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))


        # desenha caixa para marcadores
        cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
        cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
        cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
        cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)

        # calcula centro (em pixeis) do marcador
        cX = int((topLeft[0] + bottomRight[0]) / 2.0)
        cY = int((topLeft[1] + bottomRight[1]) / 2.0)
        cv2.circle(image, (cX, cY), 3, (0, 0, 255), -1)
        # desenha centro
        cv2.putText(image, str(markerID),
             (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
             0.5, (0, 255, 0), 2)
        


        cv2.putText(image, str("DETECAO ARUCO"), (0,30), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)


        #calcula distancias geometricas em pixeIs
        #LADOS
        dist_x_top = int(topRight[0]-topLeft[0])
        dist_y_top = int(topRight[1]-topLeft[1])

        dist_x_bottom = int(bottomRight[0]-bottomLeft[0])
        dist_y_bottom = int(bottomRight[1]-bottomLeft[1])

        dist_x_left = int(bottomLeft[0]-topLeft[0])
        dist_y_left = int(bottomLeft[1]-topLeft[1])

        dist_x_right = int(bottomRight[0]-topRight[0])
        dist_y_right = int(bottomRight[1]-topRight[1])

        #DIAGONAIS
        dist_x_diag02 = int(bottomRight[0]-topLeft[0])
        dist_y_diag02 = int(bottomRight[1]-topLeft[1])

        dist_x_diag13 = int(topRight[0]-bottomLeft[0])
        dist_y_diag13 = int(bottomLeft[1]-topRight[1])


        pixel_dist_aresta_cima = math.sqrt((pow(dist_x_top,2)) + (pow(dist_y_top,2)))
        pixel_dist_aresta_baixo = math.sqrt((pow(dist_x_bottom,2)) + (pow(dist_y_bottom,2)))
        pixel_dist_aresta_esquerda = math.sqrt((pow(dist_x_left,2)) + (pow(dist_y_left,2)))
        pixel_dist_aresta_direita = math.sqrt((pow(dist_x_right,2)) + (pow(dist_y_right,2)))

        pixel_dist_aresta_diag02=math.sqrt((pow(dist_x_diag02,2)) + (pow(dist_y_diag02,2)))
        pixel_dist_aresta_diag13=math.sqrt((pow(dist_x_diag13,2)) + (pow(dist_y_diag13,2)))


        #D_focal = (nr_pixels * Distance2target)/known_width
        #dist_focal_smartphone = 641.3084226 #considerando regua 17cm
        #dist_focal_smartphone = 565.8603729  #considerando regua 15cm

        dist_focal_rov_x = 546.1365183313085 #dentro de agua
        #dist_focal_rov_y = 544.4041677137612 #dentro de agua

        #dist_focal_rov_x = 538.4724543686839 #fora de agua
        #dist_focal_rov_y = 537.821572600066 #fora de agua

        #calcula distancia real
        dist_real_cima = (ARUCO_REAL_SIZE_IN_m*dist_focal_rov_x)/pixel_dist_aresta_cima
        dist_real_baixo = (ARUCO_REAL_SIZE_IN_m*dist_focal_rov_x)/pixel_dist_aresta_baixo
        dist_real_esquerda = (ARUCO_REAL_SIZE_IN_m*dist_focal_rov_x)/pixel_dist_aresta_esquerda
        dist_real_direita = (ARUCO_REAL_SIZE_IN_m*dist_focal_rov_x)/pixel_dist_aresta_direita

        #calcula distancia real das diagonais
        dist_real_diag02 = (0.141421*dist_focal_rov_x)/pixel_dist_aresta_diag02
        dist_real_diag13 = (0.141421*dist_focal_rov_x)/pixel_dist_aresta_diag13

        #calcula distancia media
        dist_med = (dist_real_cima + dist_real_baixo + dist_real_esquerda + dist_real_direita)/4
        dist_med *= 100     #para ficar em cm
        dst = int(dist_med) #para mostrar na imagem apenas valor inteiro

        #poe distancia no frame
        cv2.putText(image, str("Distancia: ")+str(dst)+str("cm"), (0,60), cv2.FONT_ITALIC, 1, (0, 0, 0), 2)

        #imprime alguma informacao na consola
        print("--------------[INFO] ArUco marker ID:{} ---------------------".format(markerID))

        print("[INFO] dist real a aruco cima: %f" %dist_real_cima)

        print("-----[INFO] dist real a aruco diag1 \: %f" %dist_real_diag02)
        print("-----[INFO] dist real a aruco diag2 /: %f" %dist_real_diag13)

        print("[INFO] dist real a aruco baixo: %f" %dist_real_baixo)
        print("[INFO] dist real a aruco esq: %f" %dist_real_esquerda)
        print("[INFO] dist real a aruco dir: %f" %dist_real_direita)

        print("[INFO] DISTANCIA MEDIA: %f cm" %dist_med)
        
        print("[INFO] Detection done in %.9f seconds" % detection_time)



# mostra output
cv2.imshow("Image", image)
# guarda imagem
#output_img = 'output_com_dist.jpg'
cv2.imwrite(output_img, image)
cv2.waitKey(0)






