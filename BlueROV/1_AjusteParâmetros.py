#from os import supports_effective_ids
#from readline import append_history_file
from re import A
from brping import definitions
from brping import PingDevice
from brping import PingMessage, PingParser
from dataclasses import dataclass
from brping import Ping360 #para inicializar
import numpy as np #para processar
import time
from argparse import ArgumentParser
import pandas as pd
#from pymavlink import mavutil

#############################################
#                                           #
#   PROG. PARA AJUSTAR DINÂMICAMENTE O ROV  #
#                                           #
#############################################


# Poderia ser preciso se quiser fazer a cena de percorrer sozinho a piscina
#master = mavutil.mavlink_connection()

#######################################################
#                   INICIALIZAÇÃO                     #
#######################################################

# Create Ping360 instance
ping360 = Ping360()

# Connect to, initialize, and set up Ping360 settings

#Serial Port
#ping360.connect_serial("/dev/ttyUSB0", 115200)

# --->>> Penso que 9090 para 1d, 9092 para 360
print("Press enter to initialize ping360 connection 192.168.2.2:9092\n")
input()

# For UDP
ping360.connect_udp("192.168.2.2", 9092)

#Inicialização
if ping360.initialize() is False:
    print("Failed to initialize Ping!\n"
    "Encerrando o programa")
    exit(1)
else: print ("Sucesso! Conexão estabelecida.\n Pronto a utilizar!\n")

#VER SE ELE RECONHECE O DISPOSITIVO CORRETO - Informações genéricas sobre o Sonar
print("Informação do dispositivo: ", ping360.get_device_information())
#imprime 'device_type':2, 'device_revision': 67, firmware (major 3, minor 1), firmware version path: 1, reserved: 0

#######################################################
#                   WELCOME/MANUAL                    #
#######################################################

print('\n##############################################\n'
'#                                            #\n'
'#    Bem vindo ao programa de controlo!      #\n'
'#                                            #\n'
'##############################################\n'

'\nEste programa apresenta os seguintes modos disponíveis:\n'
'\n* MUDAR - Mudar parâmetro(s) da configuração'
'\n* GET - Obtém leitura do ROV em .xlsx'
'\n* STATE - Devolve configuração do ROV'
'\n* SAIR')

#######################################################
#                      FUNÇÕES                        #
#######################################################

def request_simple(p):

    # Se não estiver a dar a declaração global, mudar o ping360 para p
    data = ping360.get_device_data()
    print('Dados %s', data)
        
#######################################################
#                FUNÇÕES SELETIVAS                    #
#######################################################

def mudar(p): #fazer a filtragem para que apenas sejam aceites valores dentro da gama possível

    print("Selecione o parâmetro que pretende mudar:\n"
    "   ANGULO\n"
    "   PERIODO\n"
    "   NR SAMPLES\n"
    "   FREQUENCIA\n"
    "   DUR TRANS\n"
    "   SPEED OF SOUND\n"
    "   SET MODE (NIY)\n" #Not Implemented Yet
   )

    mode = input()
    mode1 = mode.upper()

    if(mode1 == 'SPEED OF SOUND'):  # Refenir velocidade da água
        print("Nova Vel do Som na Água: ")
        vel = int(input())
        p.set_speed_of_sound(vel)

    if(mode1 == 'SET MODE'): #VER MELHOR O QUE FAZ
        print("Parâmetros: Mode, Gain, Angle, Trans Dur, Sample Period, Trans Freq, Nr os Samples")
        p.set_mode(mode)

    if(mode1 == 'ANGULO'): # Mudar angulo (de começo?)
        print("Novo angulo:")
        ang = int(input())
        p.set_angle(ang)

    if(mode1 == 'PERIODO'): # Definir novo período de amostragem - impacta na resolução das distâncias
        print("Novo periodo:")
        per = int(input())
        print(p.set_sample_period(per))

    if(mode1 == 'NR SAMPLES'): # Definir nr de samples por "direção"
        print("Novo nr de amostras:")
        samples = int(input())
        ping360.set_number_of_samples(samples)

    if(mode1 == 'FREQUENCIA'): # Definir frequência da transmissão
        print("Nova freq:")
        freq = int(input())
        p.set_transmit_frequency(freq)
        
    if(mode1 == 'DUR TRANS'): # Quanto tempo demora a transmissão do sinal
        print("Nova duracao transmissao:")
        dur = int(input())
        p.set_transmit_duration(dur)

# Falta implementar, exige uma junção de vários
def modos():  #NÃO TEM NADA IMPLEMENTADO AINDA
    print("Existem dois modos disponíveis:\n"
        "\n PERCORRER PAREDE"
        "\n RECOLHER INFORMAÇÃO 360")

    mode = input()
    mode1 = mode.upper()

    if(mode1 == 'PERCORRER PAREDE'):
        # PASSOS
        # Configurar sonar para -45 graus a 135 graus
        # Ver se distância < que um certo nr (possivelmente 0,5m)
        # Ativar motores para andar em frente. Se detetar parede a menos de 0,5m parar
        # Ativar motores laterais até ficar novamente na safe zone
        # Se detetar parede a menos de 0,5m na direção frontal. Parar
        # Efetuar rotação de 90
        # Repetir
        a = 1

def get(p): # Modos para aquisição de dados
    #os valores de data[i] aparecem entre 0-255 que são os níveis da ADC
    print("Três modos de recolha de dados:\n"
    "   0,9 deg\n"
    "   9 deg\n"
    "   free\n")

    mode = input()
    mode3 = mode.upper()
    
    f = open('testeApres3.xlsx', 'w')
    dtype = np.dtype('B')

    if(mode3 == '0,9 DEG'):  # 360 graus = 400 grads = passo de 0.9
        #p.control_auto_transmit(0,399,1,0)
        matriz = []
        tstart_s = time.time()
        # wait for 400 device_data messages to arrive
        # ---> RECEIVING <<<---
        for x in range(400):
            response = p.transmitAngle(x)
            d = []
            for i in range(80, 480):
                d.append(response.data[i])
            matriz.append(d)
            #f.write(response.bytearray)
            #f2.write(response)
            #print(response)
            #print('\n')
        tend_s = time.time()
        df = pd.DataFrame(matriz)
        df.to_excel(excel_writer = 'testeApres3.xlsx')
        # stop the auto-transmit process
        p.control_motor_off()

        f.close()

    if(mode3 == '9 DEG'):  # Recolha com um passo de 9 graus (360 graus = 40 "direções")
        #p.control_auto_transmit(0,399,10,0)
        matriz = []
        tstart_s = time.time()
        # wait for 400 device_data messages to arrive
        # ---> RECEIVING <<<---
        for x in range(400):
            response = p.transmitAngle(x)
            d = []
            for i in range(80, 480):
                d.append(response.data[i])
            matriz.append(d)
            #f.write(response.bytearray)
            #f2.write(response)
            #print(response)
            #print('\n')
        tend_s = time.time()
        df = pd.DataFrame(matriz)
        df.to_excel(excel_writer = 'testeAjusteMeioLateral.xlsx')
        # stop the auto-transmit process
        p.control_motor_off()

        f.close()

        print("full scan in %dms, %dHz" % (1000*(tend_s - tstart_s), 400/(tend_s - tstart_s)))

        # stop the auto-transmit process
        p.control_motor_off()

    if(mode3 == 'FREE'):

        print("Insira os seguintes parâmetros:\n"
        "   Start_Angle (0~399), End_Angle(0~399), Step (in Grad) (1 Grad = 0.9 Degree)\n"
        )
        #1 GRAD = 0.9 DEGREE
        s_ang, e_ang, step = input().split

        p.control_auto_transmit(s_ang,e_ang,step,0)

        tstart_s = time.time()
        # wait for 400 device_data messages to arrive
        for x in range(400):
            p.wait_message([definitions.PING360_DEVICE_DATA])
        tend_s = time.time()

        # stop the auto-transmit process
        p.control_motor_off()

        print("full scan in %dms, %dHz" % (1000*(tend_s - tstart_s), 400/(tend_s - tstart_s)))
    

############################################
###                                      ###
###                 MAIN                 ###    
###                                      ###
############################################

#Estado Inicial do Sonar - Ao iniciar o programa faz um pedido de dados para verificar os parâmetros em uso
request_simple(ping360)

# Devolve "Dados {'mode':1, 'gain_setting': 0, 'angle': 266, 'transmit_durantion': 27, 'sample_period': 222, 'transmist_frequency': 750, 'number_of_samples': 1200, bytearray(b'')}"

while True:

    mode1 = input()
    mode = mode1.upper()

    if (mode == 'STATE'):
        request_simple(ping360)
        print("\nFIM DA CHAMADA DE STATUS\nEsperando nova instrução"
            '\n* MUDAR - Mudar parâmetro(s) da configuração'
            '\n* GET - Obtém leitura do ROV em .xlsx'
            '\n* STATE - Devolve configuração do ROV'
            '\n* SAIR')

    if (mode == 'GET'):
        get(ping360)
        print("\nFIM DA CHAMADA DE STATUS\nEsperando nova instrução"
            '\n* MUDAR - Mudar parâmetro(s) da configuração'
            '\n* GET - Obtém leitura do ROV em .xlsx'
            '\n* STATE - Devolve configuração do ROV'
            '\n* SAIR')

    if (mode == 'MUDAR'):
        mudar(ping360)
        print("\nFIM DA CHAMADA DE STATUS\nEsperando nova instrução"
            '\n* MUDAR - Mudar parâmetro(s) da configuração'
            '\n* GET - Obtém leitura do ROV em .xlsx'
            '\n* STATE - Devolve configuração do ROV'
            '\n* SAIR')
        #Chama a função de mudança 


    # --->>> NÃO USAR AINDA <<<---
    if (mode == 'MODES'):
        #Chama o função para realizar uma func definida pelo user
        modos()
        print("\n PARAMETROS DEFAULT INSTALADOS:\nEsperando nova instrução"
        '\n* MUDAR'
        '\n* GET'
        '\n* DEFAULT\n')

    if (mode == 'SAIR'):
        print("\nFim da ligação. Encerrando o programa\n")
        exit(1)