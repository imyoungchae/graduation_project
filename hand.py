from time import sleep
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]
uuid = "00001801-0000-1000-8000-00805f9b34fb"
advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)
client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)
try: 
    while True:
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
                            a=str("S")
                            a1=str("S0")

                                        
                            if send_dis<100:
                                str_send=str(send_dis)
                                sock_text=a1+str_send
                                client_sock.send(sock_text)
                            else:
                                str_send=str(send_dis)
                                sock_text1=a+str_send
                                client_sock.send(sock_text1)


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
except IOError:
    pass
print("disconnected")
client_sock.close()
server_sock.close()
print("all done")
