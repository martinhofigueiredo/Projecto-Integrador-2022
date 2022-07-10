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
            i+=1
    return xacc, yacc, zacc, xgyro, ygyro, zgyro, timestamp

#   Get N samples of acceleration for x, y, z axis 
N = 10000


master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')


xacc, yacc, zacc, xgyro, ygyro, zgyro, timestamp = get_data(N, master)

f = open("teste_parado.txt", "w")
for i in range(N):
    f.write(f'{xacc[i]};{yacc[i]};{zacc[i]};{xgyro[i]};{ygyro[i]};{zgyro[i]};{timestamp[i]}\n')
f.close()