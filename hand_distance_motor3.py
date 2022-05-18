
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
                            if 45<=send_dis<=55:
                                sock.send("S050")
                                print("50")


                            elif 95<=send_dis<=105:                  
                                sock.send("S100")
                                print("100")


                            elif 195<=send_dis<=205:
                                sock.send("S200")
                                print("200")


                            elif 295<=send_dis<=305:
                                sock.send("S300")
                                print("300")


                            elif 380<=send_dis<=400:
                                sock.send("S400")
                                print("400")


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
