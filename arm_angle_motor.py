from bluetooth import *
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
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

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

# establishing a bluetooth connection
try:
    sock=BluetoothSocket( RFCOMM )
    sock.connect((target_address, port))

    while True:         
        try:
            cap = cv2.VideoCapture(0)
            ## Setup mediapipe instance
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    str2="Romote Control Robotic Arm"
                    cv2.putText(frame, str2, (80, 40), cv2.FONT_HERSHEY_COMPLEX,1, (0, 0, 255))
                    # Recolor image to RGB
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False

                    # Make detection
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
                        #sock.send(angle)
                        
                        if 15<=round_angle<=25:
                            print("20")
                            sock.send("3020")
                            
                        elif 26<=round_angle<=35:
                            print("30")
                            sock.send("3060")
                            
                        elif 36<=round_angle<=45:
                            print("40")
                            sock.send("3040")
                            
                        elif 46<=round_angle<=55:
                            print("50")
                            sock.send("3050")
                            
                        elif 56<=round_angle<=65:
                            print("60")
                            sock.send("3060")
                            
                        elif 66<=round_angle<=75:
                            print("70")
                            sock.send("3070")                            

                        elif 85<=round_angle<=95:
                            print("90")
                            sock.send("3090")

                        elif 96<=round_angle<=105:
                            print("100")
                            sock.send("3100")

                        elif 115<=round_angle<=125:
                            print("120")
                            sock.send("3120")
                            
                        elif 135<=round_angle<=145:
                            print("140")
                            sock.send("3140")                            
                           

                        elif 146<=round_angle<=155:
                            print("150")
                            sock.send("3150")
                            
                        elif 156<=round_angle<=165:
                            print("160")
                            sock.send("3160")                           

                        elif 170<=round_angle<=180:
                            print("180")
                            sock.send("3180")
                            

                        else:
                            print(round_angle)

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

                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break

                cap.release()
                #cv2.destroyAllWindows()
        
        
        except:
            print("disconnected")
            sock.close()
            print("all done")
        
except btcommon.BluetoothError as err:
    print('An error occurred : %s ' % err)
    pass
