import matplotlib.pyplot as plt
import numpy as np
import time
import os 
import fcntl

def acquire(lock_file):
    open_mode = os.O_RDONLY
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


#   Read File
#f = os.open("teste_parado.txt", "r")

L = 10000
depth = []
timestamp = []
pressure = []

plt.show()

axes = plt.gca()
axes.set_ylim(-2, 0.5)
axes.set_xlim(0, 100)
l, = axes.plot(timestamp, depth, 'r-')

for i in range(L):  
    fd = acquire('teste.txt')
    print(i)

    #obj = os.fdopen(fd)
    #line = obj.readline()
    #release(fd)
    abc = os.read(fd, 200)
    release(fd)
    #line = list(map(ifloatnt, obj.readline().split(';')))
    if abc == b'':
        continue
    line = list(map(float, abc.decode('UTF-8').split(';')))
    print(line[0])
    depth.append(-line[0])
    pressure.append(line[1])
    timestamp.append(i)

    
    l.set_xdata(timestamp)
    l.set_ydata(depth)

    #axes.set_ylim(min(depth)-50, max(depth)+50)
    #if i > 100:
    axes.set_xlim(0, i+10)
    axes.set_ylim(min(depth), max(depth))
    #plt.autoscale(enable=True, axis='both', tight=None)
    plt.draw()
    
    plt.pause(1e-17)
    time.sleep(0.1)
    

#f.close()

print(depth)
print(pressure)
print(timestamp)


"""plt.rcParams["figure.figsize"] = (10,10)
fig, (ax, ax2) = plt.subplots(2)


ax.plot(timestamp, depth)
ax.set(xlabel = 'Timestamps (s)', ylabel = 'Depth (m)')

ax2.plot(timestamp, pressure)
ax2.set(xlabel = 'Timestamps (s)', ylabel = 'Pressure (Pa)')"""


plt.show()

