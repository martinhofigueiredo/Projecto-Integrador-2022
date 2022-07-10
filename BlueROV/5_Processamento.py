from os import supports_effective_ids
from readline import append_history_file
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
import sys, re
from scipy.stats import norm
import statistics
import decode_sensor_binary as dec
from argparse import ArgumentParser

################################
#                              #
#   PROC POR DIST. GAUSSIANA   # # Não funcionou bem, foi uma primeira tentativa de processamento
#                              #
################################

# https://gist.github.com/Stormix/c4514688b69f4aad6306abe1f5c874f9

# https://stackoverflow.com/questions/28774960/how-to-get-read-excel-data-into-an-array-with-python
# d som =  v som * t sample; dist = d som / 2
# 10m = 1500 * t sample / 2; t sample max = 1000 us
# t sample = nr sample * periodo amostragem; nr sample = 0.00(6)/88e-9

def distancias(file_name, pontos):
    dist = []
    j = 0
    # Open log and begin processing
    log = dec.PingViewerLogReader(file_name)

    # Decode loop

    for index, (timestamp, decoded_message) in enumerate(log.parser()):
        if index == 0:
            # Get header information from log
            # (parser has to do first yield before header info is available)
            # print(log.header)

            # ask if processing
            yes = input("\nContinue and decode received messages? [Y/n]: \n")
            if yes.lower() in ('n', 'no'):
                break

        # Imprime só a primeira para ver se está tudo em ordem e podermos ver a estrutura

        dist.append(meters_per_sample(decoded_message) * (pontos[index]+0.5))
    
        #print(dist[j])
    
        j+=1  # Vamos fazer até j = x para fazer 1 volta completa
        if(j==L):
            return dist

    return dist

def meters_per_sample(message,  v_som = 1500): #mensagem # NÃO ESTOU A USAR

    #return v_som * mensagem.smaple_period * 12.5e-9
    # se passassemos a mensagem usavamos a de cima
    tempo = message.sample_period * 12.5e-9 # tempo entre samples
    return v_som * tempo  # message.sample_period * tirei isto. https://discuss.bluerobotics.com/t/access-ping360-data-for-post-processing-python/10416/2?fbclid=IwAR3b5eTyrtLGkpD8Ng6b3GLwTmgVlAFFw3ikhRwaQBkNwKSA1M6BT7ZTu7k

    # Retorna a distância do alvo por sample, em metros
    # Periodo de amostragem está em incrementos de 222 ns
    # tempo de voo inclui ir e voltar, é preciso dividir por 2

start = time.time()
L = 400               #   Number of directions    (with T=24ms)
N = 400               #   Samples each T
speed_sound = 1500
plt.style.use('classic')

f = open('teste.xlsx', 'r')
df = pd.read_excel('teste.xlsx')
#print(len(df))
#print(df[0][0])
#print(df)

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

### MAIN ###

sd = []
mean = []
pontos = []
z = []
dist = []

for i in range(1,L):
    z.append(i)
# Criar distribuição probabilística
# Média
for i in range(0,L):
    x = []
    for j in range(0,N):
        x.append(df[i][j]) # Faço a soma de todos em cada direção
    
    # print(x) print(len(x)) = 400
    mean.append(float(statistics.mean(x))) # Array com as médias em cada direção
    sd.append(float(statistics.stdev(x))) # Array com os desvios em cada direção
    # print("%d %d", mean[i], sd[i])
    gauss = norm.cdf(z, loc=mean[i], scale=sd[i]+0.1)  # Adicionei 0.1 sem critério algum, mas isto as vezes estava a dar 0
    #plt.plot(z, gauss)
    #plt.show()
    #plt.savefig('teste3.png')
    for k in range(0, N-1):
        if(gauss[k]>0.99):
            pontos.append(k)
            break
    #print("LEN PONTOS %d", len(pontos))

# Calcula as distâncias 
#print(pontos)
dist = distancias('20220623-122611704.bin', pontos)
print(dist)

for h in range(0,len(dist)-1):
    if (dist[h] < 0.75):
        dist[h] = 0.75

theta = 2*np.pi/400
xp = []
yp = []
for x in range(len(dist)-1):
    xp.append(dist[x] * np.cos(-x*theta))
    yp.append(dist[x] * np.sin(-x*theta))


fig2, ax2 = plt.subplots()
ax2.scatter(xp, yp, vmin=0, vmax=100)
ax2.set(xlim=(-5, 5), xticks=np.arange(-5, 5),
       ylim=(-5, 5), yticks=np.arange(-5, 5))
ax2.grid()
plt.show()

print("Processamento Feito!")

plt.savefig('teste2.png')

f.close()


#distancias = []
#for k in range(pontos):
#    distancias.append(pontos[k]*)

# https://www.researchgate.net/publication/302072080_PROBABILISTIC_FILTERING_OF_SONAR_DATA

# https://www.geeksforgeeks.org/how-to-plot-a-normal-distribution-with-matplotlib-in-python/

# https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html


