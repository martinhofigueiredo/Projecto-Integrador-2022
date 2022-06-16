from os import supports_effective_ids
from readline import append_history_file
import matplotlib.pyplot as plt
import numpy as np
import time

start = time.time()
L = 102                 #   Number of directions    (with T=24ms)
N = 470                 #   Samples each T
speed_sound = 1500
interval = 0.024/(N*2)     #   Sampling frequency
plt.style.use('_mpl-gallery-nogrid')

def filtragem(x, y, pow):
    tam = len(x)
    
    pontos = []
    for z in range(tam):
        pontos.append((x[z], y[z], pow[z]))
    
    xf2 = []
    yf2 = []
    powf2 = []
    #   Ir de quadrado em quadrado
    for i in range(-10, 10):
        for j in range(-10, 10):
            sum = 0
            indices = []
            cont_indices = 0
            tam = len(pontos)
            for z in range(tam):
                if pontos[z][0] < j or pontos[z][0] > j+1 or pontos[z][1] < i or pontos[z][1] > i+1:
                    continue
                #   Meter os valores num tuple acho que seria mais facil
                #   porque tenho que elimina-los depois
                #   talvez (x,y,pow) ? e num array guardo estes tuples
                #   e guardo os indices dos que estão no quadradop
                indices.append(z)
                sum += pontos[z][2]
                cont_indices += 1
            indices.sort(reverse=1)
            if sum < 3500:
                for w in range(cont_indices):
                    pontos.pop(indices[w])
                continue
            
            """else:
                sum_x = 0
                sum_y = 0
                powf2_aux = []
                for w in range(cont_indices):
                    sum_x += pontos[indices[w]][0]
                    sum_y += pontos[indices[w]][1]
                    powf2_aux.append(pontos[indices[w]][2])
                xf2.append(sum_x/cont_indices)
                yf2.append(sum_y/cont_indices)
                powf2.append(max(powf2_aux))"""
    
    xf = []
    yf = []
    powf = []
    tam = len(pontos)
    for i in range(tam):
        if np.sqrt(pontos[i][0]**2 + pontos[i][1]**2) > np.sqrt(40) or (pontos[i][0] < 1 and pontos[i][0] > -1 and pontos[i][1] < 1 and pontos[i][1] > -1):
            continue
        xf.append(pontos[i][0])
        yf.append(pontos[i][1])
        powf.append(pontos[i][2])
    return xf, yf, powf

def kalman(x, y, pow):
    xf, yf, powf = [], [], []
    tam = len(x)
    for w in range(tam):
        if w == 0:
            xf.append(pow[w]/255*x[w])
            yf.append(pow[w]/255*y[w])
            powf.append(pow[w]/255*pow[w])
        xf.append(xf[w-1] + pow[w]/255*(x[w] - xf[w-1]))
        yf.append(yf[w-1] + pow[w]/255*(y[w] - yf[w-1]))
        powf.append(powf[w-1] + pow[w]/255*(pow[w] - powf[w-1]))

    return xf, yf, powf




#   Read File
f = open("potencias.csv", "r")

x = []
y = []
for i in range(L):
    #x = x + list(map(int, f.readline().split(';')))
    x.append(list(map(int, f.readline().split(';'))))

for j in range(L):
    for w in range(N):
        y.append(j)
        #if x[j][w] < 40:
            #x[j][w] = 0

#   distance = known speed of sound in water * (measured time for echo to return / 2)
aux = []
d = []
for j in range(L):
    for w in range(N):
        aux.append(speed_sound * ( w*interval / 2) )
    d.append(aux)
    aux = []


#   Data for Radar plot
#   x = d*cos(theta)
#   y = d*sin(theta)
#   each sample is 360/102 degrees, so sample_n+1 = sample_n + pi/102
#                                      sample_n+1 = sample_n - theta    (clockwise)
theta = 2*np.pi/102
_x = []
_y = []
_pow = []
for i in range(L):
    for w in range(N):
        _x.append(d[i][w] * np.cos(-i*theta))
        _y.append(d[i][w] * np.sin(-i*theta))
        _pow.append(x[i][w])
        
#   filtragem

x_filtrado, y_filtrado , pow_filtrado = filtragem(_x ,_y, _pow)
x_kalman, y_kalman, pow_kalman = kalman(x_filtrado, y_filtrado, pow_filtrado)
#   Data for Samples plot
X, Y = np.meshgrid(np.linspace(-100, 100, 256), np.linspace(-100, 100, 256))
Z = x[::-1]

#   plot Samples
#fig, ax = plt.subplots()
#ax.imshow(Z)
print(f'Demorou {time.time() - start} segundos')


#   plot Radar
fig2, ax2 = plt.subplots()

fig3, ax3 = plt.subplots()

fig4, ax4 = plt.subplots()
#   s and c are number os powers

ax3.scatter(_x, _y, s=x, c=x, vmin=0, vmax=100)
ax3.set(xlim=(-10, 10), xticks=np.arange(-10, 10),
       ylim=(-10, 10), yticks=np.arange(-10, 10))

ax2.scatter(x_filtrado, y_filtrado, s=pow_filtrado, c=pow_filtrado, vmin=0, vmax=100)
ax2.set(xlim=(-10, 10), xticks=np.arange(-10, 10),
       ylim=(-10, 10), yticks=np.arange(-10, 10))

ax4.scatter(x_kalman, y_kalman, s=pow_kalman, c=pow_kalman, vmin=0, vmax=100)
ax4.set(xlim=(-10, 10), xticks=np.arange(-10, 10),
       ylim=(-10, 10), yticks=np.arange(-10, 10))

ax2.grid()
ax3.grid()
ax4.grid()
plt.show()


f.close()