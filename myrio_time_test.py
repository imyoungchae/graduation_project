from bluetooth import *
import math
import time
import datetime



#######################################################
# Scan
#######################################################

target_name = "myrio_test"   # target device name
target_address = "98:DA:D0:00:48:50"
port = 1         # RFCOMM port

nearby_devices = discover_devices()

# scanning for target device
for bdaddr in nearby_devices:
    print(lookup_name( bdaddr ))
    if target_name == lookup_name( bdaddr ):
        target_address = bdaddr
        break

if target_address is not None:
    print('device found. target address %s' % target_address)
else:
    print('could not find target bluetooth device nearby')

#######################################################
# Connect
#######################################################

# establishing a bluetooth connection
try:
    sock=BluetoothSocket( RFCOMM )
    sock.connect((target_address, port))

    while True:         
        try:
            start=time.time()
            recv_data = sock.recv(1024)
            print(recv_data)
            sock.send(recv_data)
            end=time.time()
            sec=(end-start)
            result=datetime.timedelta(seconds=sec)
            print(result)
            #sock.send("hi")
            
        except KeyboardInterrupt:
            print("disconnected")
            sock.close()
            print("all done")

except btcommon.BluetoothError as err:
    print('An error occurred : %s ' % err)
    pass
