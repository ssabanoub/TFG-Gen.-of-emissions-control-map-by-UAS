'By Abanoub Sargious -- Generacio mapa d emissions amb UAS'
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
import numpy as np
import time, sys, csv
from mq import *
from datetime import datetime

telemetria = open('telemetria.csv', 'w')
writer = csv.writer(telemetria, delimiter=',')
telemetria.write('Hora, Latitud, Longitud, Altura, Nivell CO')
telemetria.write('\n')

connection_string = 'udp:192.168.1.100:14550'
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


    def data_callback():
        perc = mq.MQPercentage()
        loc = vehicle.location.global_frame
        time = datetime.now().time()
        print("%s, %s, %s, %s, %s" % (time,loc.lat,loc.lon,loc.alt, perc["CO"]))
        data = np.asarray([time,loc.lat, loc.lon, loc.alt, perc["CO"]])
        writer.writerow(data)


#Main program

try:
    print("Press CTRL+C to End Mission.")
    while True:
        data_callback()
        time.sleep(5)

except KeyboardInterrupt:
    print("\nAbort by user")
    telemetria.close()
    vehicle.close()
    print("Mission completed")
    time.sleep(10)

