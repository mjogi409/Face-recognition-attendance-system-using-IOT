
#module importing

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import serial
import time
#for send
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
#---------------------------------
#Logic
#---------------------------------
#ardruino

# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM4', 9800, timeout=1)
time.sleep(2)

def reader(ser):
    line = ser.readline()  # read a byte
    if line:
        string = line.decode()
        nums = string.split(' cm')[0]  # convert the byte string to a unicode string
        print(int(nums))
        if (int(nums) > 10):



#---------------------------------
#path
            path = 'photos'
            images = []
            personNames = []
            myList = os.listdir(path)
            print(myList)
            #---------------------------------
            for cu_img in myList:
                current_Img = cv2.imread(f'{path}/{cu_img}')
                images.append(current_Img)
                personNames.append(os.path.splitext(cu_img)[0])
            print(personNames)
            #---------------------------------
            #marking attendance in database
            def markAttendance2(name, inTime, inDate):
                with open('Attendance.csv', 'r+') as f:
                    myDataList = f.readlines()
                    nameList = []
                    for line in myDataList:
                        entry = line.split(',')
                        nameList.append(entry[0])
                    if name not in nameList:
                        time_now = datetime.now()
                        tStr = time_now.strftime('%H:%M:%S')
                        dStr = time_now.strftime('%d/%m/%Y')
                        f.writelines(f'\n{name},{tStr},{dStr}')
            #---------------------------------
            def faceEncodings(images):
                encodeList = []
                for img in images:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(img)[0]
                    encodeList.append(encode)
                return encodeList

            encodeListKnown = faceEncodings(images)
            print("ALl encodings complete!!!")

            cap = cv2.VideoCapture(0)

            def record(cap):
                ret,frame =cap.read()
                faces = cv2.resize(frame, (0,0), None, 0.25,0.25)
                faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

                facesCurrentFrame = face_recognition.face_locations(faces)
                encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

                for encodeFace, faceloc in zip(encodesCurrentFrame, facesCurrentFrame):
                    matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
                    matchIndex = np.argmin(faceDis)

                    if matches[matchIndex]:
                        name = personNames[matchIndex].upper()
                        #print(name)
                        y1,x2,y2,x1 = faceloc
                        y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                        cv2.rectangle(frame, (x1,y2-35), (x2,y2), (0,255,0), cv2.FILLED)
                        cv2.putText(frame, name,(x1 + 6,y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)

                        inTime = datetime.now().time()
                        inDate = datetime.now().date()
                        markAttendance2(name,str(inTime),str(inDate))
                cv2.imshow("Attendance",frame)

                if cv2.waitKey(10) == 13:
                    return 'complete'


                else:
                    record(cap)
            record(cap)
            cap.release()
            cv2.destroyAllWindows()



        else:
            reader(ser)

reader(ser)
ser.close()
