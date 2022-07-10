import serial
import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d
from matplotlib.animation import FuncAnimation
import psutil
import collections

class stateVector:
    def __init__(self):
        self.posx = []
        self.posy = []
        self.posz = []

        self.velx = []
        self.vely = []
        self.velz = []
        
        self.accx = []
        self.accy = []
        self.accz = []

        self.noisex = 0
        self.noisey = 0
        self.noisez = 0

def kalman(sv, xraw, yraw, zraw):
    ax, ay, az = 0, 0, 0
    vx, vy, vz = 0, 0, 0
    KGAINX = 0.5
    KGAINY = 0.5
    path = list()
    path.append(list())
    path.append(list())
    sv.accx = smoother(xraw)
    sv.accy = smoother(yraw)
    for i in range(0, len(sv.accx)):
        #if i == 0:
            #---    Divide by 9800 because IMU data is in mG (g * 10**-3 = 9.8 * 10**-3)
        sv.accx.append( sv.accx[i-1] + KGAINX * (xraw[i]/9800 - sv.accx[i-1]) )
        sv.accy.append( sv.accy[i-1] + KGAINY * (yraw[i]/9800 - sv.accy[i-1]) )
        #sv.accz.append( sv.accz[i-1] + KGAIN * (zraw[i]/9800 - sv.accz[i-1]) )

        sv.velx.append(sv.accx[i]*dt)
        sv.vely.append(sv.accy[i]*dt)
        #sv.velz.append(sv.accz[i]*dt)

        #------ Calculo da posicao
        if i < 2:
            sv.posx.append(0)
            sv.posz.append(0)
            sv.posy.append(0)
            path[0].append(0)
            path[1].append(0)
            continue
        #---    Maior que valor esperado??
        if abs((sv.accx[i] - sv.accx[i-2])/dt) > 2:
            ax = (sv.accx[i] - sv.accx[i-2]) / 2
        else:
            ax = 0
        if abs((sv.accy[i] - sv.accy[i-2])/dt) > 2:
            ay = (sv.accy[i] - sv.accy[i-2]) / 2
        else:
            ay = 0
        
        if abs((sv.velx[i] - sv.velx[i-2])/dt) > 2:
            vx = (sv.velx[i] - sv.velx[i-2]) / 2
        else:
            vx = 0
        if abs((sv.vely[i] - sv.vely[i-2])/dt) > 2:
            vy = (sv.vely[i] - sv.vely[i-2]) / 2
        else:
            vy = 0

        #--- Kalman for position
        """sv.posx.append( sv.posx[i-1] + ( (sv.accx[i] - sv.accx[i-1])/(sv.accx[i] + sv.accx[i-1]) ) * (vx*dt + ax*dt*dt/2 - sv.posx[i-1]) )
        sv.posy.append( sv.posy[i-1] + ( (sv.accy[i] - sv.accy[i-1])/(sv.accy[i] + sv.accy[i-1]) ) * (vy*dt + ay*dt*dt/2 - sv.posy[i-1]) )
        sv.posz.append( sv.posz[i-1] + KGAIN * (vz*dt + az*dt*dt/2 - sv.posz[i-1]) )"""

        xdev = vx*dt + 0.5*ax*dt*dt
        ydev = vy*dt + 0.5*ay*dt*dt
        #---    vetor posx e posy guardam desvios
        sv.posx.append(xdev)
        sv.posy.append(ydev)
        if sv.posx[i] == sv.posx[i-1] == 0 or sv.posy[i] == sv.posy[i-1] == 0:
            path[0].append(path[0][i-1])
            path[1].append(path[1][i-1])
            continue
        path[0].append(path[0][i-1] + KGAINX * (xdev - path[0][i-1]))
        path[1].append(path[1][i-1] + KGAINY * (ydev - path[1][i-1]))
        #KGAINX = sv.noisex / ( sv.noisex + (path[0][i] - path[0][i-1]) / (path[0][i] + path[0][i-1] ))
        #KGAINY = sv.noisey / ( sv.noisey + (path[1][i] - path[0][i-1]) / (path[0][i] + path[0][i-1] ))
    
    return path

def kalman2(sv, xraw, yraw, zraw):
    path = list()
    path.append(list())
    path.append(list())
    KGAIN = 0.1
    #   Smoother Raw Acel
    smooth_x = smoother(xraw)
    smooth_y = smoother(yraw)

    L = len(smooth_x)
    #sf1 = interp1d(range(0,L), smooth_x, kind='quadratic')
    #f2 = interp1d(range(0,L), smooth_y, kind='quadratic')
    starting_point = [0, 0]

    path[0].append(starting_point[0])
    path[1].append(starting_point[1])

    #   a -> aceleracao raw(depois de filtro kalman) interpolada
    """a = list()
    b = list()
    for i in range(0, L):
        a.append(f1(i)[()])
        b.append(f2(i)[()])"""

    ax = 0
    vx = 0
    px = 0
    ay = 0
    vy = 0
    py = 0
    k1 = 1
    k2 = 1
    px0 = 0
    py0 = 0
    vy0 = 0
    vx0 = 0
    for i in range(1,L):
        
        """#atualizar ax quando ?
        if ((smooth_x[i] + smooth_x[i-1]) / 2 - ax)/(k1*dt) >= 2 or ((smooth_x[i] + smooth_x[i-1]) / 2 - ax)/(k1*dt) <= -2:
            ax = (smooth_x[i] - smooth_x[i-1]) / 2
            print(f'ax: {ay}\n')
            vx = vx0 + ax*dt
            vx0 = vx
            k1 = 0"""
        ax = (smooth_x[i] - smooth_x[i-1]) / 2
        vx = vx0 + ax*dt
        vx0 = vx
        if ax <= 10 and ax >= -10:
            ax = 0
            vx = 0
            k1 = 0

        """if ((smooth_y[i] + smooth_y[i-1]) / 2 - ay)/(k2*dt) >= 2 or ((smooth_y[i] + smooth_y[i-1]) / 2 - ay)/(k2*dt) <= -2:
            ay = (smooth_y[i] - smooth_y[i-1]) / 2
            print(f'ay: {ay}\n')
            vy = vy0 + ay*dt
            vy0 = vy
            k2 = 0"""

        ay = (smooth_y[i] - smooth_y[i-1]) / 2
        vy = vy0 + ay*dt
        vy0 = vy

        if ay <= 10 and ay >= -10:
            ay = 0
            vy = 0
            k2 = 0

        """if a[i] <= 30 and a[i] >= -30:
            a[i] = 0
        if b[i] <= 30 and b[i] >= -30:
            b[i] = 0"""


        """if( (a[i] - ax) / (k1*dt) >= 5 or (a[i] - ax) / (k1*dt) <= -5 ):
            ax = a[i]
            px0 = px
        if( (b[i] - ay) / (k2*dt) >= 5 or (b[i] - ay) / (k2*dt) <= -5 ):
            ay = b[i]
            py0 = py"""
        
        

        
        k1 += 1
        k2 += 1

        px = path[0][i-1] + vx*dt + 0.5*ax*dt*dt    
        py = path[1][i-1] + vy*dt + 0.5*ay*dt*dt 
        


        path[0].append(path[0][i-1] + KGAIN * (px - path[0][i-1]))  
        path[1].append(path[1][i-1] + KGAIN * (py - path[1][i-1]))

    """plt.plot(range(0,L), smooth_x, 'o', range(0,L), f(range(0,L)), '-')
    plt.legend(['data', 'linear'], loc='best')
    plt.show()"""
    return path

def smoother(func):
    smoothered = list()
    #---    N point average
    N = 7

    for i in range(int(N/2)-1, len(func)):
        smoothered.append(sum(func[i-int(N/2)-1:i+int(N/2)-1])/N)

    return smoothered

def anim(i):
    #clear axis
    ax.cla()
    print(f'i = {i}')
    #plot 
    if(i > 999):
        ani.pause()

    ax.plot(path[0][0:i], path[1][0:i])
    ax.scatter(path[0][i], path[1][i])

sv = stateVector()


dt = 1/100

stabilize_samples = 250
N_SAMPLES = 1000
gain = 0.95
k = 0
i=0
xraw=list()
zraw=list()
yraw=list()
t=list()
xlow_pass = list()
ylow_pass = list()
zlow_pass = list()

ser = serial.Serial('/dev/ttyACM0',115200)
ser.close()
ser.open()

#---   Stabilize samples
while k < stabilize_samples:
    if i < 7:
        data = ser.readline()
        i += 1
        continue
    
    data = ser.readline()
    sv.noisex = (sv.noisex+float(data.decode())) / 2
    data = ser.readline()
    sv.noisey = (sv.noisey+float(data.decode())) / 2
    data = ser.readline()
    sv.noisez = (sv.noisez+float(data.decode())) / 2
    
    print(f'Stabilizing {k / stabilize_samples * 100}%')
    print(f'noisex: {sv.noisex}')
    k += 1

#---    Capture samples
k = 0
while k < N_SAMPLES:
    #---    
    t.append(k)

    data = ser.readline()
    xraw.append(float(data.decode()))

    data = ser.readline()
    yraw.append(float(data.decode()))

    data = ser.readline()
    zraw.append(float(data.decode()))
    
    #---    Low Pass Filter
    if k == 0:
        xlow_pass.append(xraw[k]-sv.noisex)
        ylow_pass.append(yraw[k]-sv.noisey)
        zlow_pass.append(zraw[k]-sv.noisez)
        k+=1
        continue
    
    xlow_pass.append( (gain*xlow_pass[k-1]) + (1.0-gain)*(xraw[k]-sv.noisex) )
    ylow_pass.append( (gain*ylow_pass[k-1]) + (1.0-gain)*(yraw[k]-sv.noisey) )
    zlow_pass.append( (gain*zlow_pass[k-1]) + (1.0-gain)*(zraw[k]-sv.noisez) )
    #---
    print(f'Amostra {k} : ( {xraw[k]} , {xlow_pass[k]} )')
    k += 1 



plot0 = plt.figure(0)
plt.plot(t, xraw) 
plt.title("Raw accel")

plot1 = plt.figure(1)
plt.plot(t, xlow_pass)
plt.title("Low pass accel + kalman filter")

path = kalman2(sv, xlow_pass, yraw, zraw)

plot2 = plt.figure(2)
ax = plt.subplot(111)

plt.scatter(path[1], path[0])
plt.title("Low pass + Kalman pos")

#ani = FuncAnimation(plot2, anim, interval=1)


plt.show()
