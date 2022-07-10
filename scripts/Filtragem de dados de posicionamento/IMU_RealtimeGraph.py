import numpy as np
import time
import matplotlib.pyplot as plt

"""
Example of how to filter for specific mavlink messages coming from the
autopilot using pymavlink.

Can also filter within recv_match command - see "Read all parameters" example
"""
# Import mavutil
from pymavlink import mavutil
import time

# Create the connection
# From topside computer
def get_data(N, connection):
    i = 0
    xacc, yacc, zacc = [], [], []
    xgyro, ygyro, zgyro = [], [], []
    timestamp = []
    t1, t2 = 0, 0
    #-------------------Initialize PLOT----------
    y = []
    x = []
        
    y.append(0)
    x.append(0)
    delta_time = 0.1

    
    """figure, ax = plt.subplots(figsize=(8,6))
    line1, = ax.plot(x, y)

    plt.title("Dynamic Plot of gyro",fontsize=25)

    plt.xlabel("X",fontsize=18)
    plt.ylabel("Y",fontsize=18)   """ 
    #--------------------------------------------

    while i < N:
        t1 = time.time()
        msg = connection.recv_match()
        
        if not msg:
            continue
        if msg.get_type() == 'SCALED_IMU2':
            if i == 0:
                t0 = msg.time_boot_ms
            print("\033c", end="")
            #   Frequency +/-= 10Hz
            print(f'yacc: {msg.yacc}')
            print(f'xacc: {msg.xacc}')
            print(f'zacc: {msg.zacc}')
            print(f'xgyro: {msg.xgyro}')
            print(f'ygyro: {msg.ygyro}')
            print(f'zgyro: {msg.zgyro}')
            print(f'timestamp: {msg.time_boot_ms - t0}ms')
            #   Gyroscope   (mrad/s)
            xgyro.append(msg.xgyro)
            ygyro.append(msg.ygyro)
            zgyro.append(msg.zgyro)
            #   Acceleration    (mG) G=9.81m/s^2
            yacc.append(msg.yacc)
            xacc.append(msg.xacc)
            zacc.append(msg.zacc)
            #   Time    (ms)
            timestamp.append(msg.time_boot_ms - t0)
            print(f'SAMPLE NUMBER {i}')
            t2 = t1
           
            x.append(xgyro[i]*delta_time + x[i-1])
            y.append(ygyro[i]*delta_time + y[i-1])
            #--------UPDATE PLOT---------
            print(f'i = {i}')
            updated_y = x[i]
            updated_x = timestamp[i]
            
            plt.scatter(updated_x, updated_y)
            plt.title("GYROMOVEMENT")
            plt.xlabel("x")
            plt.ylabel("y")
            plt.show()
            i+=1
        plt.show()
            
    return xacc, yacc, zacc, xgyro, ygyro, zgyro, timestamp

#   Get N samples of acceleration for x, y, z axis 
N = 1000


master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')


xacc, yacc, zacc, xgyro, ygyro, zgyro, timestamp = get_data(N, master)



