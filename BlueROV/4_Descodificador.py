import decode_sensor_binary as dec
from argparse import ArgumentParser
import csv
import pandas as pd
import xlsxwriter

###############################################
#                                             #
#   DESCODIFICADOR DE LOGS FROM PING VIEWER   #
#                                             #
###############################################
#                                             #
#      RECEBE .BIN --->>> DEVOLVE .XLSX       #
#                                             #
###############################################

# Declarações e Inicializações
f = open('teste0446.xlsx', 'w')
j = 0
matriz = []

# Parse arguments
parser = ArgumentParser(description=__doc__)   # Recebe e guarda o nome do ficheiro
parser.add_argument("file",
                    help="File that contains PingViewer sensor log file.")
args = parser.parse_args()

# Open log and begin processing
log = dec.PingViewerLogReader(args.file)
print(dir(log))

# Decode loop

for index, (timestamp, decoded_message) in enumerate(log.parser()):
    if index == 0:  # Faz print do header da primeira mensagem e pergunta se queremos continuar
        # Get header information from log
        # (parser has to do first yield before header info is available)
        print(log.header)

        # ask if processing
        yes = input("Continue and decode received messages? [Y/n]: ")
        if yes.lower() in ('n', 'no'):
            break

    # Imprime só a primeira para ver se está tudo em ordem e podermos ver a estrutura

    #if 290<j<300:  # DESCOMENTAR se quisermos ver a marca temporal e um exemplo de como chegam os dados
    #   print('timestamp:', repr(timestamp))
    #   print(decoded_message)
    
    d = []
    l = []
    #if(j>100): #Só vamos recolher de 100 para a frente por causa de ser um pouco confuso o log do labview
    if(j>=600): # O Ping Viewer estava configurado de forma genérica, e no começo as amostras são um pouco confusas, pelo que apanhamos um outro ciclo completo (360 graus) mais para a "frente"
        for i in range(580,980):  #Vel água = 1500m/s; # Estamos a recolher na gama de 580 a 980 que é uma gama restrita, sensivelmente entre 2 e 3.5m
            d.append(decoded_message.data[i])
        matriz.append(d)  # Matriz de arrays
    
    j+=1  # Vamos fazer até j = x para fazer 1 volta completa
    if(j==1000):
        break
        
    #print(decoded_message.data[0])
    #print('\n')
    # uncomment to confirm continuing after each message is printed  <<<----
    #out = input('q to quit, enter to continue: ')
    #if out.lower() == 'q': break

# https://stackoverflow.com/questions/31909722/how-to-write-python-array-into-excel-spread-sheet

# print(matriz) # Podemos fazer print da matriz se quisermos ver se os dados estão coerentes com os do excel

df = pd.DataFrame(matriz)
df.to_excel(excel_writer = 'teste0446.xlsx') # Colocamos no excel xlsx

print("Fim de Operação\n")

### INFORMAÇÕES SOBRE O ROV ###
# Nr samples 1200
# Sample Period 222
# Transmit Duration 27
# Transmit Freq 750 kHz
# Mode 1
# Server address ('192.168.2.2', 9092)
# Angle 0.9 graus = 1 gradiano

# distancia = vel som * (tempo medido * 2)
# 0 < dist < 8
# temp max = 8/1500 = 0,00533 s
# 27 us. 

# Sample Period - Time interval between individual signal intensity 
#samples in 25 ns increments (80 to 40000 == 2 to 1000 us)

# https://gist.github.com/Stormix/c4514688b69f4aad6306abe1f5c874f9
# https://docs.bluerobotics.com/ping-protocol/pingmessage-ping360/
# https://docs.bluerobotics.com/ping-protocol/pingmessage-ping360/
# https://pythonguides.com/scipy-normal-distribution/