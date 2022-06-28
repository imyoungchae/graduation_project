import cv2
import mediapipe as mp
import numpy as np
from bluetooth import *

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

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 
try:
    sock=BluetoothSocket( RFCOMM )
    sock.connect((target_address, port))


                cap = cv2.VideoCapture(0)

                while cap.isOpened():
                        success, image = cap.read()
                        if not success:
                            continue

                        with mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:

                            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                            results = hands.process(image)

                            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                            if results.multi_hand_landmarks:
                                for hand_landmarks in results.multi_hand_landmarks:
                                    thumb = hand_landmarks.landmark[4]
                                    index = hand_landmarks.landmark[8]

                                    diff = abs(index.x - thumb.x)

                                    volume = int(diff * 500)
                                    a=str("S")
                                    a1=str("S0")

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
                                        image, text='Distance: %d' % volume, org=(30, 50),
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                                        color=255, thickness=2)

                                    mp_drawing.draw_landmarks(
                                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                            ret, frame = cap.read()

                            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            image.flags.writeable = False

                            results = pose.process(image)

                                        # Recolor back to BGR
                            image.flags.writeable = True
                            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                                        # Extract landmarks
                            try:
                                landmarks = results.pose_landmarks.landmark

                                            # Get coordinates
                                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                                            # Calculate angle
                                angle = calculate_angle(shoulder, elbow, wrist)
                                round_angle=round(angle,0)
                                sock.send(3000+angle)

                                # Visualize angle
                                cv2.putText(image, str(angle), 
                                                tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                                    )
                            except:
                                pass
                                                                # Render detections
                                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                                            )  


                        cv2.imshow('Mecha Graduation Project', image)
                        if cv2.waitKey(1) == ord('q'):
                            break

                cap.release()

        except:
            print("disconnected")
            sock.close()
            print("all done")
        
except btcommon.BluetoothError as err:
    print('An error occurred : %s ' % err)
    pass
