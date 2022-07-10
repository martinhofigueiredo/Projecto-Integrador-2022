from os import supports_effective_ids
from readline import append_history_file
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
import sys, re
from scipy import stats

# https://stackoverflow.com/questions/28774960/how-to-get-read-excel-data-into-an-array-with-python

start = time.time()
L = 400                 #   Number of directions    (with T=24ms)
N = 400                 #   Samples each T
speed_sound = 1500
interval = 0.024/(N*2)     #   Sampling frequency
#plt.style.use('_mpl-gallery-nogrid') original
#plt.rcParams['interactive'] == True - supostamente isto ativava as imagens
plt.style.use('classic')

f = open('teste.xlsx', 'r')
df = pd.read_excel('teste.xlsx')
print(df[0][0])
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

mean = []
cov = []

# Criar distribuição probabilística

# Média
for i in range(0,L-2):
    m = 0
    for j in range(0,N-2):
        m += df[i][j]
    mean.append((m/L))
    #print('Media %d', i)
    #print(mean[i])
    #print('\n')
    
    for j in range(0,N-2):
        sum = (df[i][j] - mean[i])**2
    cov.append(np.sqrt(sum/(N-3)))

    # print("Par média-cov2 por direção: %d-%d",mean[i], cov[i])

    # Create a normal distribution
    snd = stats.norm(mean[i], cov[i])

    #
    #Plot the standard normal distribution for different values of random variable
    # falling in the range -100, 100
    #
    #plt.figure(figsize=(7.5,7.5))
    plt.plot(df[i], snd.pdf(df[i]))
    plt.xlim(252, 255)
    plt.title('Normal Distribution (Mean = , STD = )', fontsize='15')
    plt.xlabel('Values of Random Variable X', fontsize='15')
    plt.ylabel('Probability', fontsize='15')
    plt.show()

    if(i == 10):
        print("mean %d, std %d", mean[i], cov[i])
        plt.savefig('teste2.png')


# https://www.researchgate.net/publication/302072080_PROBABILISTIC_FILTERING_OF_SONAR_DATA


