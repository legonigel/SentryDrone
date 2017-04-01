print "Initiallizing..."
print "Please remember that Drone Footage and Internet is necessary for this code to work."

from collections import deque
import cv2
import numpy as np
import argparse
from pyasn1.compat.octets import null
import time

import boto
from boto.s3.key import Key

#optional argument
def nothing(x):
    pass

# NOTE: Internet necessary for this part of code to work
def pushToBucket(count):
    c = boto.connect_s3()
    b = c.get_bucket('cokecount') 
    k = Key(b)
    k.key = 'count'
    
    k.set_contents_from_string(str(count))
    
    #print "Bucket info: " + k.get_contents_as_string()

cam = cv2.VideoCapture('tcp://192.168.1.1:5555')

ret = True

show_hsv = False
show_glitch = False

print "Camera capture initialized, entering loop..."

while(True):
    obj = []
    ret, frame = cam.read()
    if not ret:
        print "Trying again to read from camera..."
        time.sleep(.1)
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    prevgray = gray
    
    Gaussianframe=cv2.GaussianBlur(frame,(5,5),0)
    
    #convert to HSV from BGR
    hsv=cv2.cvtColor(Gaussianframe, cv2.COLOR_BGR2HSV)
    
    hul = 0
    huh = 3
    sal = 170
    sah = 222
    val = 0
    vah = 255
    
    #make array for final values
    HSVLOW=np.array([hul,sal,val])
    HSVHIGH=np.array([huh,sah,vah])
    
    #apply the range on a mask
    mask = cv2.inRange(hsv,HSVLOW, HSVHIGH)
    
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=5)
    
    res = cv2.bitwise_and(Gaussianframe,Gaussianframe, mask =mask)
    
    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
        
    center = None
    
    for c in cnts:
        if len(c) > 3:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            
            M = cv2.moments(c)
            if not(M["m00"] == 0):
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            if cv2.contourArea(c) > 20 and radius > 100:
                obj.append((x,y))
                cv2.circle(Gaussianframe, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(Gaussianframe, center, 1, (0, 0, 255), -1)
    
    #print "trying to push to bucket..."
    pushToBucket(len(obj))
    cv2.imshow('image', res)
    cv2.imshow('blobs', Gaussianframe)
    #time.sleep(.1)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        print "Quitting...!"
        break
    
cam.release()
cv2.destroyAllWindows()

print "Closed."