#The video and coordinate files are not on the github
import cv2
import pickle
import cvzone
import numpy as np
import pyodbc
import pandas as pd

# Video feed
cap = cv2.VideoCapture('carPark.mp4')

#Connects to the sql
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=LAPTOP-DJ90VA3F\MSSQLSERVER01;'
                      'Database=master;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
 
 #opens a video
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)
 
width, height = 107, 48
 
def checkParkingSpace(imgPro):
    global loop2
    global loop3
    spaceCounter = 0
    
    for pos in posList:
        x, y = pos
 
        imgCrop = imgPro[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)

 
 
        if count < 900: #this makes it green/unoccpied
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            #sql -- having trouble here becasue sql takes a little bit of time to execute so the video can only play at 1/2 speed
            #I am going to make it so the server only gets updated every minute to fix this problem
            cursor.execute("UPDATE ParkingSpace SET Occupancy = {} WHERE ParkingSpace = {}".format(2,posList.index(pos)))
            conn.commit()
                
        else: #this makes it red/unoccupied
            color = (0, 0, 255)
            thickness = 2
            #sql -- having trouble here becasue sql takes a little bit of time to execute so the video can only play at 1/2 speed
            #I am going to make it so the server only gets updated every minute to fix this problem
            cursor.execute("UPDATE ParkingSpace SET Occupancy = {} WHERE ParkingSpace = {}".format(1,posList.index(pos)))
            conn.commit()
 
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)
 
    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))
while True:
 
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
 
    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    #cv2.imshow("ImageBlur", imgBlur)
    #cv2.imshow("ImageThres", imgMedian)
    cv2.waitKey(10)
