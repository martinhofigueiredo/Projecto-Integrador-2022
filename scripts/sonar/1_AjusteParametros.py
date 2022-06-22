#from os import supports_effective_ids
#from readline import append_history_file
from re import A
from brping import definitions
from brping import PingDevice
from brping import PingMessage, PingParser
from dataclasses import dataclass
from brping import Ping360 #para inicializar
#from brping import decode_sensor_binary
#from decode_sensor_binary import PingViewerLogReader, Ping360Settings
import numpy as np #para processar
import time
from argparse import ArgumentParser
#from pymavlink import mavutil
import csv
import os


open_mode = os.O_CREAT | os.O_RDWR | os.O_TRUNC
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

#VER SE ELE RECONHECE O DISPOSITIVO CORRETO
print("Informação do dispositivo: ", ping360.get_device_information())
#imprime 'device_type':2, 'device_revision': 67, firmware (major 3, minor 1), firmware version path: 1, reserved: 0

#######################################################
#                   WELCOME/MANUAL                    #
#######################################################

print('##############################################\n'
'#                                            #\n'
'#    Bem vindo ao programa de controlo!      #\n'
'#                                            #\n'
'##############################################\n'

'\nEste programa apresenta os seguintes modos disponíveis:\n'
'\n* SET'
'\n* GET'
'\n* DEFAULT'
'\n* SAIR')

#######################################################
#                      FUNÇÕES                        #
#######################################################

def request_simple(p):

    # Se não estiver a dar a declaração global, mudar o ping360 para p
    data = ping360.get_device_data()
    print("Estado do Sonar")#, ping360._data())
    print('Dados %s', data)

""" def writer():
    # Parse arguments
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("file",
                        help="File that contains PingViewer sensor log file.")
    args = parser.parse_args()

    # Open log and begin processing
    log = PingViewerLogReader(args.file)

    for index, (timestamp, decoded_message) in enumerate(log.parser()):
        if index == 0:
            # Get header information from log
            # (parser has to do first yield before header info is available)
            print(log.header)

            # ask if processing
            yes = input("Continue and decode received messages? [Y/n]: ")
            if yes.lower() in ('n', 'no'):
                break

        print('timestamp:', repr(timestamp))
        print(decoded_message) """
        # uncomment to confirm continuing after each message is printed
        #out = input('q to quit, enter to continue: ')
        #if out.lower() == 'q': break
        
#######################################################
#                FUNÇÕES SELETIVAS                    #
#######################################################

def set(p): #fazer a filtragem para que apenas sejam aceites valores dentro da gama possível

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

    if(mode1 == 'SPEED OF SOUND'):
        print("Nova Vel do Som na Água: ")
        vel = input()
        p.set_speed_of_sound(vel)

    if(mode1 == 'SET MODE'): #VER MELHOR O QUE FAZ
        print("Parâmetros: Mode, Gain, Angle, Trans Dur, Sample Period, Trans Freq, Nr os Samples")
        p.set_mode(mode)

    if(mode1 == 'ANGULO'):
        print("Novo angulo:")
        ang = input()
        p.set_angle(ang)

    if(mode1 == 'PERIODO'):
        print("Novo periodo:")
        per = input()
        p.set_sample_period(per)

    if(mode1 == 'NR SAMPLES'):
        print("Novo nr de amostras:")
        samples = int (input())
        p.set_number_of_samples(samples)

    if(mode1 == 'FREQUENCIA'):
        print("Nova freq:")
        freq = int (input())
        p.set_transmit_frequency(freq)
        
    if(mode1 == 'DUR TRANS'):
        print("Nova duracao transmissao:")
        dur = input()
        p.set_transmit_duration(dur)

def modos():  #NÃO TEM NADA IMPLEMENTADO AINDA
    print("Existem dois modos disponíveis:\n"
        "\n PERCORRER PAREDE"
        "\n RECOLHER INFORMAÇÃO 360")

def get(p): #TESTAR 0,8 E 9 E 0,9
    #os valores de data[i] aparecem entre 0-255 que são os níveis da ADC
    print("Três modos de recolha de dados:\n"
    "   0,9 deg\n"
    "   9 deg\n"
    "   free\n")

    mode = input()
    mode3 = mode.upper()
    
    f = os.open('teste.csv', open_mode)
    writer = csv.writer(f)

    if(mode3 == '0,9 DEG'):
        p.control_auto_transmit(750,420,0,399,1,0)

        tstart_s = time.time()
        # wait for 400 device_data messages to arrive
        # ---> RECEIVING <<<---
        for x in range(400):
            response = p.transmitAngle(x)
            print(response)
            writer.writerow(response)
        tend_s = time.time()

        # stop the auto-transmit process
        p.control_motor_off()

        f.close()

    if(mode3 == '0,8 DEG'):
        p.control_auto_transmit(0,399,1,0)

        tstart_s = time.time()
        # wait for 400 device_data messages to arrive
        for x in range(400):
            p.wait_message([definitions.PING360_DEVICE_DATA])
        tend_s = time.time()

        #Print do relatório
        print("full scan in %dms, %dHz" %(1000*(tend_s - tstart_s), 400/(tend_s - tstart_s)))

        # stop the auto-transmit process
        p.control_motor_off()

    if(mode3 == '9 DEG'):
        p.control_auto_transmit(start_angle = 0, stop_angle = 399, num_steps = 1, delay = 0)

        tstart_s = time.time()
        # wait for 400 device_data messages to arrive
        # ---> RECEIVING <<<---
        for x in range(40):
            dados = p.transmitAngle(x)
            print(dados)
        tend_s = time.time()

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

#Estado Inicial do Sonar
request_simple(ping360)

while True:

    mode1 = input()
    mode = mode1.upper()

    if(mode == 'SAVE DATA'):
        # Parse arguments
        parser = ArgumentParser(description=__doc__)
        parser.add_argument("BlueRov\teste_csv",
                        help="File that contains PingViewer sensor log file.")
        args = parser.parse_args()

        # Open log and begin processing
        log = PingViewerLogReader(args.file)

        for index, (timestamp, decoded_message) in enumerate(log.parser()):
            if index == 0:
                # Get header information from log
                # (parser has to do first yield before header info is available)
                print(log.header)

                # ask if processing
                yes = input("Continue and decode received messages? [Y/n]: ")
                if yes.lower() in ('n', 'no'):
                    break

            print('timestamp:', repr(timestamp))
            print(decoded_message)
            # uncomment to confirm continuing after each message is printed
            #out = input('q to quit, enter to continue: ')
            #if out.lower() == 'q': break

    if (mode == 'GET'):
        get(ping360)
        print("\nFIM DA CHAMADA DE STATUS\nEsperando nova instrução"
        '\n* SET'
        '\n* GET'
        '\n* DEFAULT\n')

    if (mode == 'SET'):
        set(ping360)
        print("\n FIM DA OPERAÇÃO REQUISITADA\nEsperando nova instrução"
        '\n* SET'
        '\n* GET'
        '\n* DEFAULT\n')
        #Chama a função de mudança 


    # --->>> NÃO USAR AINDA <<<---
    if (mode == 'MODES'):
        #Chama o função para realizar uma func definida pelo user
        modos()
        print("\n PARAMETROS DEFAULT INSTALADOS:\nEsperando nova instrução"
        '\n* SET'
        '\n* GET'
        '\n* DEFAULT\n')

    if (mode == 'SAIR'):
        print("Fim da ligação. Encerrando o programa\n")
        exit(1)

