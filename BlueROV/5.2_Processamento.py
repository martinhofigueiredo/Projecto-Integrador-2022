from os import supports_effective_ids
from readline import append_history_file
from matplotlib import style  # Gráficos
import matplotlib.pyplot as plt # Gráficos
import numpy as np # Processamento matemático
import time # Tempo
import pandas as pd # Estruturas para os dados
import sys, re
import math # Funções matemáticas 
import decode_sensor_binary as dec # Descodificador - acho que aqui não é usado
from argparse import ArgumentParser # Parser - também não é usado neste

#################################### ###################################
#                                  # #       PROCESSAMENTO PARA        #
#       PROC. POR THRESHOLD        # #      LEITURAS FEITAS PELO       #
#                                  # #     1_Ajuste de Parâmetros      #
#################################### ###################################

# Da próxima vez, o melhor é fazer tudo em funções para ser mais fácil de reutilizar em outros códigos

# Os dados foram guardados só com as amostras acima de 80, devido ao ROV só conseguir ler a mais de 0.75m

# Possíveis pares de parâmetros
# 500 samples = 480 Sample Period = 9mm resolução
# 550 samples = 436 Sample Period = 8,175mm resolução
# 480 samples = 500 Sample Period = 9,375mm resolução <<<--- Opção Usada
# 450 samples = 535 Sample Period = 10,03mm resolução

# https://gist.github.com/Stormix/c4514688b69f4aad6306abe1f5c874f9
# https://stackoverflow.com/questions/28774960/how-to-get-read-excel-data-into-an-array-with-python

# Fórmula de cálculo
# dist = d som / 2
# d som =  v som * t sample
# t sample = nr sample * periodo amostragem
# periodo de amostragem = nr de ticks * duração de 1 tick (25e-9)

def comprimento(a,b):  # Cálculo das distâncias
    return math.dist(a,b)

def perp( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def seg_intersect(a1,a2, b1,b2) : # Cálculo da interseção
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    return (num / denom.astype(float))*db + b1

def distancias(pontos): # Cálculo das distâncias das leituras
    dist = []
    j = 0
    for i in range(L):
        dist.append(meters_per_sample() * (pontos[i]+offset+0.5)) # o 0.5 é para estar a meio da sample, uma espécie de distância média

    return dist

def meters_per_sample(v_som = 1500): # Cálculo da resolução

    #return v_som * mensagem.smaple_period * 12.5e-9
    sample_period = 500
    tempo = sample_period * 12.5e-9 # tempo entre samples
    return v_som * tempo  
    # https://discuss.bluerobotics.com/t/access-ping360-data-for-post-processing-python/10416/2?fbclid=IwAR3b5eTyrtLGkpD8Ng6b3GLwTmgVlAFFw3ikhRwaQBkNwKSA1M6BT7ZTu7k

    # Retorna a distância do alvo por sample, em metros
    # Periodo de amostragem está em incrementos de 222 ns
    # tempo de voo inclui ir e voltar, é preciso dividir por 2, daí usar 12.5e-9 para a duração dos ticks

start1 = time.time() # Tempo Total
L = 400               # Number of directions 
N = 400               # Samples each T - (entre 80 e 480)
offset = 80           # Samples descartadas
speed_sound = 1500    # Velocidade do som na água
plt.style.use('classic') 

f = open('testeAjuste.xlsx', 'r') # Ficheiro para escrita
df = pd.read_excel('testeAjuste.xlsx') # Data frame para processar os dados
#print(len(df))
#print(df[0][0])
#print(df)

# Cada grau é uma coluna -> nos ficheiros do log, nestes ainda tenho de ver

"""      Unnamed: 0    0    1    2    3  ...  395  396  397  398  399
0             0   80  155  202  235  ...    0    0    2    2    3
1             1   87  157  203  236  ...   22   21   22   27   28
2             2   69  146  196  232  ...    0    0    0    0    0
3             3   67  145  197  231  ...    0    0    0    0    0
4             4   66  146  195  231  ...    0    0    0    0    0
..          ...  ...  ...  ...  ...  ...  ...  ...  ...  ...  ...
394         394  255  255  255  255  ...    0    0    0    0    0
395         395  255  255  255  255  ...   25   16    0    0    0
396         396  255  255  255  255  ...    0    0    8    8    5
397         397  255  255  255  255  ...    0    0    0    0    0
398         398  255  255  255  255  ...    7    0    0    0    0 """

################
#              #
#     MAIN     #
#              #
################

#print(df[10][0])
#print(df[10][1])
#print(df[10][2])
#print(df[10][3])
#print(df[10][4]) O primeiro índice é a coluna

# Inicializações
pontos = []
dist = []

# Filtragem dos pontos para tratamento
start2 = time.time() # Tempo Filtragem

for i in range(0,L):
    max = 50  # Limite mínimo da leitura considerado "aceitável"  
    max_pos = 0 # Índice da sample
    for j in range(5,N-5):  # Por este método estamos a descartar estas distâncias (a que corresponde às primeiras 5 leituras e 5 últimas, mas é algo que o método precisa para funcionar)
        if(df[j][i] >= max):
            count = 0
            for h in range(-5,5):
                if(df[j+h][i]>(df[j][i]-20)): # 20 é o threshold
                    count+=1
            if(count>=5):  # Para evitar falsas leituras, estamos a exigir que pelo menos metade dos pontos próximos estejam acima da janela de threshold
                max = df[j][i]
                max_pos = j
    pontos.append(max_pos)  # Guardamos um array com as posições dos índices em cada direção

# Calcula as distâncias 
dist = distancias(pontos)
print(len(dist))
print(len(pontos)) # Apenas informação de debug para ver se as 400 direções foram aceites
#print(pontos)
#print(dist)

#for h in range(0,len(dist)-1):  # Deixou de ser necessário por já estarmos a descartar as amostrasm que podiam ter estas distâncias
#   if (dist[h] < 0.75):
#      dist[h] = 0.75

# Processamento
start3 = time.time() # Tempo Processamento

theta = 2*np.pi/L # Cálculo do passo
xp = []
yp = []
for x in range(len(dist)-1): # Cálculo das coordenadas x, y de cada leitura
    xp.append(dist[x] * np.cos(-x*theta)) 
    yp.append(dist[x] * np.sin(-x*theta))
    
# Desenho da Piscina - exige que a leitura tenha sido feita na perperndicular a um dos lados
start4 = time.time() # Tempo Desenho

x1 = xp[0]
x2 = xp[100]
x3 = xp[200]
x4 = xp[300]
y1 = yp[0]
y2 = yp[100]
y3 = yp[200]
y4 = yp[300]
#print(x1) 2.06
#print(x2) 0

# Arrays para seleção dos pontos das retas
ret1 = []
ret1y = []
ret2 = [] 
ret2y = []
ret3 = []
ret3y = []
ret4 = [] 
ret4y = []
ret5 = [] 
ret5y = []
ret6 = [] 
ret6y = []
ret7 = [] 
ret7y = []
ret8 = [] 
ret8y = []

for i in range(len(dist)-1):
    if(x1-0.1 < xp[i] < x1+0.1): # Usamos novamente uma janela de threshold, neste caso de pontos que estejam sensivelmente abaixo ou acima 0.1
        ret1.append(xp[i])
        ret1y.append(yp[i])
    if(x2-0.1 < xp[i] < x2+0.1):
        ret2.append(xp[i])
        ret2y.append(yp[i])
    if(x3-0.1 < xp[i] < x3+0.1):
        ret3.append(xp[i])
        ret3y.append(yp[i])
    if(x4-0.1 < xp[i] < x4+0.1):
        ret4.append(xp[i])
        ret4y.append(yp[i])

    if(y1-0.1 < yp[i] < y1+0.1):
        ret5.append(xp[i])
        ret5y.append(yp[i])
    if(y2-0.1 < yp[i] < y2+0.1):
        ret6.append(xp[i])
        ret6y.append(yp[i])
    if(y3-0.1 < yp[i] < y3+0.1):
        ret7.append(xp[i])
        ret7y.append(yp[i])
    if(y4-0.1 < yp[i] < y4+0.1):
        ret8.append(xp[i])
        ret8y.append(yp[i])

print(len(ret1y))
print(len(ret3y))
print(len(ret6y))
print(len(ret8y))
print(len(ret2y))
print(len(ret4y))
print(len(ret5y))
print(len(ret7y))

#print(ret1)
#print(ret1y)

fig3, ax3 = plt.subplots()

i = -5
x = []
while(i<5):
    x.append(i)
    i+=0.1 # Array de pontos de x, entre -5 e 5 espaçados de 0.1

alpha1 = []
alpha2 = []
alpha3 = []
alpha4 = []
alpha5 = []
alpha6 = []
alpha7 = []
alpha8 = []
zero1 = 0
zero3 = 0
zero6 = 0
zero8 = 0

if(len(ret1) > 30):  # Processamento. Caso tenha mais de 30 pontos, considera-se que há ali uma reta
    print("Reta 1")
    A = np.vstack([ret1, np.ones(len(ret1))]).T
    y = np.array([ret1y]).T
    alpha1 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha1)
    w = alpha1[0]*x + alpha1[1]
    ax3.plot(x, w, lw = 2,  c='blue')
if(len(ret2) > 30):
    print("Reta 2")
    A = np.vstack([ret2, np.ones(len(ret2))]).T
    y = np.array([ret2y]).T
    alpha2 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha2)
    w = alpha2[0]*x + alpha2[1]
    ax3.plot(x, w, lw=2,  c='blue')
if(len(ret3) > 30):
    print("Reta 3")
    A = np.vstack([ret3, np.ones(len(ret3))]).T
    y = np.array([ret3y]).T
    alpha3 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha3)
    w = alpha3[0]*x + alpha3[1]
    ax3.plot(x, w,lw=2,  c='blue')
if(len(ret4) > 30):
    print("Reta 4")
    A = np.vstack([ret4, np.ones(len(ret4))]).T
    y = np.array([ret4y]).T
    alpha4 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha4)
    w = alpha4[0]*x + alpha4[1]
    ax3.plot(x, w, lw=2, c='blue')
if(len(ret5) > 30):
    print("Reta 5")
    A = np.vstack([ret5, np.ones(len(ret5))]).T
    y = np.array([ret5y]).T
    alpha5 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha5)
    w = alpha5[0]*x + alpha5[1]
    ax3.plot(x, w, lw=2, c='green')
if(len(ret6) > 30):
    print("Reta 6")
    A = np.vstack([ret6, np.ones(len(ret6))]).T
    y = np.array([ret6y]).T
    alpha6 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha6)
    w = alpha6[0]*x + alpha6[1]
    ax3.plot(x, w, lw=2, c='green')
if(len(ret7) > 30):
    print("Reta 7")
    A = np.vstack([ret7, np.ones(len(ret7))]).T
    y = np.array([ret7y]).T
    alpha7 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha7)
    w = alpha7[0]*x + alpha7[1]
    ax3.plot(x, w, lw=2, c='green')
if(len(ret8) > 30):
    print("Reta 8")    
    A = np.vstack([ret8, np.ones(len(ret8))]).T
    y = np.array([ret8y]).T
    alpha8 = np.dot((np.dot(np.linalg.inv(np.dot(A.T,A)),A.T)),y)
    print(alpha8)
    w = alpha8[0]*x + alpha8[1]
    ax3.plot(x, w, lw=2, c='green')
 
# https://pythonnumericalmethods.berkeley.edu/notebooks/chapter16.04-Least-Squares-Regression-in-Python.html

p1 = []
p2 = []
p3 = []
p4 = []
p5 = []
p6 = []
p7 = []
p8 = []

# https://stackoverflow.com/questions/3252194/numpy-and-line-intersections

# Cálculo dos pontos de interseção

if(len(ret1)>30):  # Ou temos interseção entre 1 3 6 8
    p1 = np.array([x[0],alpha1[0]*x[0]+alpha1[1]], dtype=object)
    p2 = np.array([x[-1],alpha1[0]*x[-1]+alpha1[1]], dtype=object)
    p3 = np.array([x[0],alpha6[0]*x[0]+alpha6[1]], dtype=object)
    p4 = np.array([x[-1],alpha6[0]*x[-1]+alpha6[1]], dtype=object)
    p5 = np.array([x[0],alpha3[0]*x[0]+alpha3[1]], dtype=object)
    p6 = np.array([x[-1],alpha3[0]*x[-1]+alpha3[1]], dtype=object)
    p7 = np.array([x[0],alpha8[0]*x[0]+alpha8[1]], dtype=object)
    p8 = np.array([x[-1],alpha8[0]*x[-1]+alpha8[1]], dtype=object)
    inters1 = seg_intersect( p1,p2, p3,p4)
    inters2 = seg_intersect( p1,p2, p7,p8)
    inters3 = seg_intersect( p5,p6, p3,p4)
    inters4 = seg_intersect( p5,p6, p7,p8)

if(len(ret2)>30): # Ou entre 2 4 5 7
    p1 = np.array([x[0],alpha2[0]*x[0]+alpha2[1]], dtype=object)
    p2 = np.array([x[-1],alpha2[0]*x[-1]+alpha2[1]], dtype=object)
    p3 = np.array([x[0],alpha5[0]*x[0]+alpha5[1]], dtype=object)
    p4 = np.array([x[-1],alpha5[0]*x[-1]+alpha5[1]], dtype=object)
    p5 = np.array([x[0],alpha4[0]*x[0]+alpha4[1]], dtype=object)
    p6 = np.array([x[-1],alpha4[0]*x[-1]+alpha4[1]], dtype=object)
    p7 = np.array([x[0],alpha7[0]*x[0]+alpha7[1]], dtype=object)
    p8 = np.array([x[-1],alpha7[0]*x[-1]+alpha7[1]], dtype=object)
    inters1 = seg_intersect( p1,p2, p3,p4)
    inters2 = seg_intersect( p1,p2, p7,p8)
    inters3 = seg_intersect( p5,p6, p3,p4)
    inters4 = seg_intersect( p5,p6, p7,p8)

# Desenho dos pontos no gráfico

ax3.scatter(xp, yp, vmin=0, vmax=100)
ax3.scatter(inters1[0], inters1[1], lw=4, color='orange')
ax3.scatter(inters2[0], inters2[1], lw=4, color='orange')
ax3.scatter(inters3[0], inters3[1], lw=4, color='orange')
ax3.scatter(inters4[0], inters4[1], lw=4, color='orange')

#Labels

plt.annotate("Ponto_1", (inters1[0], inters1[1]), fontsize = 10)
plt.annotate("Ponto_2", (inters2[0], inters2[1]), fontsize = 10)
plt.annotate("Ponto_3", (inters3[0], inters3[1]), fontsize = 10)
plt.annotate("Ponto_4", (inters4[0], inters4[1]), fontsize = 10)

# Cálculo das dimensões da piscina

dist1 = np.abs(comprimento(inters1, inters2))
dist2 = np.abs(comprimento(inters2, inters4))
dist3 = np.abs(comprimento(inters4, inters3))
dist4 = np.abs(comprimento(inters3, inters1))

# Legenda

plt.legend(['Dist1_2: {:.3f}m'.format(dist1), 'Dist2_4: {:.3f}m'.format(dist2),'Dist4_3: {:.3f}m'.format(dist3),'Dist3_1: {:.3f}m'.format(dist4)], fancybox=True,shadow=1, loc='upper right', fontsize=10)

# Amostras e dimensões do gráfico

ax3.set(xlim=(-5, 5), xticks=np.arange(-5, 5),
       ylim=(-5, 5), yticks=np.arange(-5, 5))

# Posição do ROV -> Ivan

# Erro do processamento
media1 = (dist1 + dist3)/2
media2 = (dist2 + dist4)/2
erro1 = (np.abs(dist1-media1)/media1)*100
erro2 = (np.abs(dist3-media1)/media1)*100
erro3 = (np.abs(dist2-media2)/media2)*100
erro4 = (np.abs(dist4-media2)/media2)*100

print("Erro nas paredes 1-2: {:.3f}% e 4-3: {:.3f}%".format(erro1,erro2) )
print("Erro nas paredes 2-4: {:.3f}% e 3-1: {:.3f}%".format(erro3,erro4) )

x1 = -alpha1[1]/alpha1[0]
x3 = -alpha3[1]/alpha3[0]
dif3 = np.abs(x1-x3)
dif4 = np.abs(alpha6[1] - alpha8[1])
erro5 = ((np.abs(4.58-dif3))/4.58)*100
erro6 = ((np.abs(4.40-dif4))/4.40)*100

print("Erro de distância na horizontal em percentagem:")
print(erro6)
print("Erro de distância na vertical em percentagem:")
print(erro5)

ax3.grid()
plt.show()

plt.savefig('testeAjuste10.png')

#fig2, ax2 = plt.subplots()
#ax2.scatter(xp, yp, vmin=0, vmax=100)
#ax2.set(xlim=(-5, 5), xticks=np.arange(-5, 5),
#       ylim=(-5, 5), yticks=np.arange(-5, 5))
#ax2.grid()
#plt.show()

print("Processamento Feito!")

#plt.savefig('testeAjuste.png')

f.close()

print(f'Total - Demorou {time.time() - start1} segundos')
print(f'Leitura - Demorou {start2 - start1} segundos')
print(f'Filtragem - Demorou {start3 - start2} segundos')
print(f'Processamento - Demorou {start4 - start3} segundos')
print(f'Desenhos - Demorou {time.time() - start4} segundos')

# https://www.researchgate.net/publication/302072080_PROBABILISTIC_FILTERING_OF_SONAR_DATA

# https://www.geeksforgeeks.org/how-to-plot-a-normal-distribution-with-matplotlib-in-python/

# https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html


