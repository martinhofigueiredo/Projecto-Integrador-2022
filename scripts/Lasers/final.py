# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 22:28:53 2022

@author: Utilizador
"""

import math
from cmath import sin
from turtle import distance

import cv2
import numpy as np
from cv2 import bitwise_and
from scipy.ndimage import zoom
import gi

if _name_ == '_main_':
    # Create the video object
    # Add port= if is necessary to use a different one
    video = Video(port=4777)
    
    
    def Resolve_image(image):
        img = cv2.imread(path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        ## mask of green (36,25,25) ~ (86, 255,255)
        # mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
        mask = cv2.inRange(hsv, (36, 25, 25), (86, 255,255))
        ## slice the green
        imask = mask>0
        green = np.zeros_like(img, np.uint8)
        #cv2.imshow("mask.png", green)
        green[imask] = img[imask]
        gray = cv2.cvtColor(green, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray.png", gray)
        key = cv2.waitKey(0)#pauses for 3 seconds before fetching next image
        if key == 27:#if ESC is pressed, exit loop
                   cv2.destroyAllWindows()
        blur = cv2.GaussianBlur(gray, (5, 5),cv2.BORDER_DEFAULT)
        #cv2.imshow("blur.png", blur)
        key = cv2.waitKey(0)#pauses for 3 seconds before fetching next image
        if key == 27:#if ESC is pressed, exit loop
                   cv2.destroyAllWindows()
        
        return blur
    
    def centro_repetido(cx, cy,x):    
        if (len(x)>1):    
            for k in range(len(x[0])):
                for j in range(len(x)):
                    print(x[j][k])
                    if (x[j][k]-x[j][k]<5):
                        return 1              
        return 0
        
    
    
    
    
    
    def Calculate_pixel_distance(image,blur):
        ret, thresh = cv2.threshold(blur, 190, 255, cv2.THRESH_BINARY_INV)
        #cv2.imshow("trhes.png", thresh)
        key = cv2.waitKey(0)#pauses for 3 seconds before fetching next image
        if key == 27:#if ESC is pressed, exit loop
                   cv2.destroyAllWindows()
        contours, hierarchies = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)     
        blank = np.zeros(thresh.shape[:2],dtype='uint8')
        #cv2.imshow("blank  page", blank)  
        key = cv2.waitKey(0)#pauses for 3 seconds before fetching next image
        if key == 27:#if ESC is pressed, exit loop
                   cv2.destroyAllWindows()
        cv2.drawContours(blank, contours, -1, (255, 0, 0), 1)
        #cv2.imshow("contours in blank page", blank)  
        key = cv2.waitKey(0)#pauses for 3 seconds before fetching next image
        if key == 27:#if ESC is pressed, exit loop
                   cv2.destroyAllWindows()
        #cv2.imshow("a", blank)
        alpha=0
        centers=[]
        c=1
        for i in contours:
            M = cv2.moments(i)
            #print(M)
            if c<len(contours):
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    print(f"x: {cx} y: {cy}") 
                    if not centro_repetido(cx,cy,centers):
                        centers.append([cx,cy])
                        #print(f"apende     x: {cx} y: {cy}") 
                        cv2.circle(image, (cx, cy), 7, (0, 0, 255), -1)
                        cv2.putText(image, "center", (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        alpha=alpha+1
                        cv2.imshow("primeira imagem blur", image)
                        key = cv2.waitKey(0)#pauses for 3 seconds before fetching next image
                        if key == 27:#if ESC is pressed, exit loop
                            cv2.destroyAllWindows()
              
            c=c+1
        if len(centers) >=2:
                    dx= centers[0][0] - centers[1][0]
                    dy = centers[0][1] - centers[1][1]
                    D = np.sqrt(dx*dx+dy*dy)
           
        return D, alpha;
    
    def calcular_distancia_real(a):
        distancia_focal=546.137
        largura_real=75.00
        altura=(distancia_focal*largura_real)/(a*1000)
        return altura
    
    
        # Wait for the next frame
        while not video.frame_available():
            continue
    
        image = video.frame()
    
        
        
        blur=Resolve_image(image)
        D, alpha =Calculate_pixel_distance(image,blur)
        print("distancia entre pixeis", D)
        
        if (alpha==2 and D>0):
            Distancia_real=calcular_distancia_real(D)
            print(f"Distanica_real: {Distancia_real} ")
        else:
            print("erro")