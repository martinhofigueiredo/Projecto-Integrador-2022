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
def get_data(connection, sensor_type):
    pressure = 0
    depth = 0
    while 1:
        msg = connection.recv_match()
        #lastT=time.time()
        if not msg:
            continue
        
        #   get pressure

        if msg.get_type() == sensor_type:
            #   Frequency +/-= 10Hz
            
            if sensor_type == 'SCALED_PRESSURE2':
            #   Pressure    (hPa / 100 = Pa)            
                pressure = msg.press_abs*100
                return pressure

            elif sensor_type == 'SCALED_IMU2':
                ### gyro readings in milliRadians/second -> save values as Radians/second
                #dT = lastT - time.time()
                xgyro, ygyro, zgyro = msg.xgyro/1000, msg.ygyro/1000, msg.zgyro/1000
                xacc, yacc, zacc = msg.xacc/ (9.8 * 0.001), msg.yacc/ (9.8 * 0.001), msg.zacc / (9.8 * 0.001)
                return xgyro, ygyro, zgyro, xacc, yacc, zacc
    return pressure