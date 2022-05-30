from bluetooth import *
from time import sleep
import cv2
import mediapipe as mp

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


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

#######################################################
# Connect
#######################################################
# establishing a bluetooth connection
try:
    sock=BluetoothSocket( RFCOMM )
    sock.connect((target_address, port))

    while True:         
        try:
            with mp_hands.Hands(
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as hands:

                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        continue

                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    results = hands.process(image)

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            thumb = hand_landmarks.landmark[4]
                            index = hand_landmarks.landmark[8]

                            diff = abs(index.x - thumb.x)

                            distance = int(diff * 500)

                            send_dis=distance*3
                            
                            a=str("s")
                            a1=str("s0")
                            
                            #print("%s%d"%('s',send_dis))
                            if send_dis<100:
                                str_send=str(send_dis)
                                sock_text=a1+str_send
                                sock.send(sock_text)
                            else:
                                str_send=str(send_dis)
                                sock_text1=a+str_send
                                sock.send(sock_text1)

                            cv2.putText(
                                image, text='Distance: %d' % distance, org=(30, 50),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                                color=1, thickness=2)

                            mp_drawing.draw_landmarks(
                                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    cv2.imshow('Mecha Graduation Project', image)
                    if cv2.waitKey(1) == ord('q'):
                        break

                cap.release()
    
        except KeyboardInterrupt:
                print("disconnected")
                sock.close()
                print("all done")

except btcommon.BluetoothError as err:
    print('An error occurred : %s ' % err)
    pass
