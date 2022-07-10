"""
Example of how to filter for specific mavlink messages coming from the
autopilot using pymavlink.

Can also filter within recv_match command - see "Read all parameters" example
"""
# Import mavutil
from pymavlink import mavutil
import time
import os 
import fcntl
import math as m
import pressure_help
def acquire(lock_file):
    open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
    fd = os.open(lock_file, open_mode)

    pid = os.getpid()
    lock_file_fd = None
    
    timeout = 5.0
    start_time = current_time = time.time()
    while current_time < start_time + timeout:
        try:
            # The LOCK_EX means that only one process can hold the lock
            # The LOCK_NB means that the fcntl.flock() is not blocking
            # and we are able to implement termination of while loop,
            # when timeout is reached.
            # More information here:
            # https://docs.python.org/3/library/fcntl.html#fcntl.flock
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            pass
        else:
            lock_file_fd = fd
            break
        print(f'  {pid} waiting for lock')
        time.sleep(1.0)
        current_time = time.time()
    if lock_file_fd is None:
        os.close(fd)
    return lock_file_fd


def release(lock_file_fd):
    # Do not remove the lockfile:
    #
    #   https://github.com/benediktschmitt/py-filelock/issues/31
    #   https://stackoverflow.com/questions/17708885/flock-removing-locked-file-without-race-condition
    fcntl.flock(lock_file_fd, fcntl.LOCK_UN)
    os.close(lock_file_fd)
    return None



# Create the connection
# From topside computer
def get_data(N, connection):
    i = 0
    pressure = []
    timestamp = []
    depth_kalman = []
    depth = []

    #pressure.append(atmospheric_pressure / 100)
    depth_kalman.append(0)
    depth.append(0)
    p0 = 101325
    while i < N:
        msg = connection.recv_match()
        if not msg:
            continue
        
        print("\033c", end="")
        """if msg.get_type() == 'ATTITUDE_QUATERNION':
            if i == 0:
                t0 = msg.time_boot_ms

            q1 = msg.q1
            q2 = msg.q2
            q3 = msg.q3
            q4 = msg.q4
            print(f'quaternion ({q1},{q2},{q3},{q4})')"""
        #   get pressure
        if msg.get_type() == 'SYS_STATUS':
            battery = msg.voltage_battery
            remaining = msg.battery_remaining
        if msg.get_type() == 'SCALED_PRESSURE2':
            if i == 0:
                t0 = msg.time_boot_ms
                #   Frequency +/-= 10Hz
            #   Atmosferic pressure calibration

            #   Pressure    (hPa / 100 = Pa)
            print(f'BATTERY VOLTAGE = {battery/1000} V')
            print(f'BATERY REMAINING = {remaining} %')
            print(f'pressure: {msg.press_abs*100} Pa')

            pressure.append(msg.press_abs)
            #   Depth (m)
            #   P = rho*g*h
            #   h = P / (rho * g) -> h = depth
            depth.append((msg.press_abs*100 - p0) / (rho_freshawater * g))
        
        
            print(f'depth: {depth[-1]} m')
            #   Time    (ms)
            print(f'timestamp: {msg.time_boot_ms - t0} ms')
            timestamp.append(msg.time_boot_ms - t0)
            print(f'SAMPLE NUMBER {i}')
            i+=1
            
            fd = acquire('teste.txt')
            os.write(fd, bytes(f'{depth[i-1]};{pressure[i-1]};{timestamp[i-1]}\n', "UTF-8"))
            release(fd)
        
        """#   get IMU
        if msg.get_type() == 'SCALED_IMU2':
            if i == 0:
                t0 = msg.time_boot_ms

            accelerationZ = msg.zacc / (9.8*0.001) # (mG = 9.8*10⁻³ = 5)
            accelerationX = msg.xacc / (9.8*0.001)
            accelerationY = msg.yacc / (9.8*0.001)

            pitch = 180 * m.atan (accelerationX/m.sqrt(accelerationY*accelerationY + accelerationZ*accelerationZ))/m.pi
            roll  = 180 * m.atan (accelerationY/m.sqrt(accelerationX*accelerationX + accelerationZ*accelerationZ))/m.pi
            yaw   = 180 * m.atan (accelerationZ/m.sqrt(accelerationX*accelerationX + accelerationZ*accelerationZ))/m.pi

            print(f'yaw = {yaw}')
            print(f'pitch = {pitch}')
            print(f'roll = {roll}')
            print(f'accelerationZ = {accelerationZ}')
            print(f'accelerationY = {accelerationY}')
            print(f'accelerationX = {accelerationX}')

            #fd_imu = open('imu.txt', 'w')
            #fd_imu.writeline(f'{yaw};{pitch};{roll};{accelerationZ};{accelerationX};{accelerationY}')
            #os.write(fd_imu, bytes(f'{yaw};{pitch};{roll};{accelerationZ};{accelerationX};{accelerationY}'), "UTF-8")
            #close(fd_imu)
        if msg.get_type() == 'ATTITUDE_QUATERNION':
            if i == 0:
                t0 = msg.time_boot_ms

            q1 = msg.q1
            q2 = msg.q2
            q3 = msg.q3
            q4 = msg.q4
            print(f'quaternion ({q1},{q2},{q3},{q4})')
        if msg.get_type() == 'HIGHRES_IMU':
            if i == 0:
                t0 = msg.time_boot_ms
            print(f'HighresIMU')
            print(f'acc: ({msg.xacc},{msg.yacc},{msg.zacc}) m/s/s')
            print(f'gyro: ({msg.xgyro},{msg.ygyro},{msg.zgyro}) rad/s')
            print(f'ABS_PRESSURE: {msg.abs_pressure*100} Pa')
            print(f'temperature: {msg.temperature} C')"""
    return pressure, depth, timestamp


#   Get N samples of pressure  
N = 10000
atmospheric_pressure = 1013.25 #hPa
rho_freshawater = 997.0474 #kg.m^-3
g = 9.80665 #m.s^-2
p0 = 99000 #Pa

master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')



#   pressure, depth, timestamps
p, d, t = get_data(N, master)



"""for i in range(N):
    f.write(f'{p[i]};{t[i]}\n')
    f_depth.write(f'{d[i]};{t[i]}\n')"""


#f.close()
