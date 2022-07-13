# Import mavutil
from curses.ascii import isdigit
from pymavlink import mavutil
import time

# Create the connection
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

# Wait a heartbeat before sending commands
master.wait_heartbeat()

str_dg = input("Enter Rotation Degrees: ")
str_m = input("Enter Meters to Move: ")

dg=float(str_dg)
m=float(str_m)

print(dg,m)

rt = dg/46.024
mvft = m/0.347787

#Arms the ROV
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0)
print('ARMED!\n')

# x movement => [-1000:1000] (0 for neutral)
# y movement => [-1000:1000] (0 for neutral)
# z movement => [0:1000] (500 for neutral)
# r movement (YAW) => [-1000:1000] (0 for neutral)
# buttons => [0:15]

#Rotates the ROV

timeout_rt=float(time.time())+rt

while True:
    master.mav.manual_control_send(
        master.target_system,
        0,
        0,
        500,
        250,
        0)
    if float(time.time())>timeout_rt:
        break

master.mav.manual_control_send(
        master.target_system,
        0,
        0,
        500,
        -250,
        0)
time.sleep(0.3)

#Moves the ROV forward

timeout_mvf=float(time.time())+mvft

while True:
    master.mav.manual_control_send(
        master.target_system,
        500,
        0,
        500,
        0,
        0)
    if float(time.time())>timeout_mvf:
        break

master.mav.manual_control_send(
        master.target_system,
        -1000,
        0,
        500,
        0,
        0)
time.sleep(0.3)

# Disarms the ROV
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 0, 0, 0, 0, 0, 0, 0)
print('DISARMED!\n')