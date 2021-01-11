from dronekit import connect, VehicleMode, Command
from pymavlink import mavutil  # Needed for command message definitions
import time
import numpy as np
import random
from datetime import datetime
import csv

connection_string = 'tcp:127.0.0.1:5762'
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

telemetria = open('telemetria_simulada.csv', 'w')
writer = csv.writer(telemetria, delimiter=',')
telemetria.write('Hora, Latitud, Longitud, Altura, Nivell CO, Nivell LPG')
telemetria.write('\n')


def readmission(aFileName):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist = []
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i == 0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray = line.split('\t')
                ln_index = int(linearray[0])
                ln_currentwp = int(linearray[1])
                ln_frame = int(linearray[2])
                ln_command = int(linearray[3])
                ln_param1 = float(linearray[4])
                ln_param2 = float(linearray[5])
                ln_param3 = float(linearray[6])
                ln_param4 = float(linearray[7])
                ln_param5 = float(linearray[8])
                ln_param6 = float(linearray[9])
                ln_param7 = float(linearray[10])
                ln_autocontinue = int(linearray[11].strip())
                cmd = Command(0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2,
                              ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(aFileName):
    """
    Upload a mission from a file.
    """
    # Read mission from file
    missionlist = readmission(aFileName)

    print("\nUpload mission from a file: %s" % aFileName)
    # Clear existing mission from vehicle
    print(' Clear mission')
    cmds = vehicle.commands
    cmds.clear()
    # Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    vehicle.commands.upload()


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:  # Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)


def data_callback():
    co_simulated = random.randint(1, 15)
    if vehicle.commands.next == 5:
        co_simulated = random.randint(15, 30)
    elif vehicle.commands.next >= 6:
        co_simulated = random.randint(30, 50)
    loc = vehicle.location.global_frame
    tt = datetime.now().time()
    print("%s, %s, %s, %s, %s" % (tt,loc.lat,loc.lon,loc.alt, co_simulated))
    data = np.asarray([tt,loc.lat, loc.lon, loc.alt, co_simulated])
    writer.writerow(data)


try:
    print("Press CTRL+C to End Mission.")
    upload_mission('pla_vol.waypoints')
    arm_and_takeoff(30)
    vehicle.mode = VehicleMode('AUTO')
    while True:
        data_callback()
        time.sleep(3)

except KeyboardInterrupt:
    print("\nAbort by user")
    telemetria.close()
    vehicle.close()
    print("Mission completed")
    time.sleep(10)