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

aws_upload = 0
object_count = 0
target_center = 0,0
    
hl = 0
hh = 9
sl = 176
sh = 240
vl = 0
vh = 255

#make array for final values
rHSVLOW=np.array([hl,sl,vl])
rHSVHIGH=np.array([hh,sh,vh])

hl = 107
hh = 115
sl = 138
sh = 291
vl = 0
vh = 255

#make array for final values
bHSVLOW=np.array([hl,sl,vl])
bHSVHIGH=np.array([hh,sh,vh])
        
#optional argument
def nothing(x):
    pass

# NOTE: Internet necessary for this part of code to work
def pushToBucket():
    global target_center, object_count
    c = boto.connect_s3()
    b = c.get_bucket('cokecount')
    k = Key(b)
    k.key = 'count'
    k.set_contents_from_string(str(object_count))
    
    b = c.get_bucket('targetxandydata')
    k = Key(b)
    k.key = 'x'
    k.set_contents_from_string(str(target_center[1]))
    k.key = 'y'
    k.set_contents_from_string(str(target_center[0]))
    #print "Bucket info: " + k.get_contents_as_string()

cam = cv2.VideoCapture('tcp://192.168.1.1:5555')

ret = True

show_hsv = False
show_glitch = False

print "Camera capture initialized, entering loop..."

while(True):
    obj = []
    ret, frame = cam.read()
    
    if ret:
    
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        prevgray = gray
        
        Gaussianframe=cv2.GaussianBlur(frame,(5,5),0)
        
        #convert to HSV from BGR
        hsv=cv2.cvtColor(Gaussianframe, cv2.COLOR_BGR2HSV)
        
        #apply the range on a mask
        mask_r = cv2.inRange(hsv,rHSVLOW, rHSVHIGH)
        mask_b = cv2.inRange(hsv,bHSVLOW, bHSVHIGH)
        
        #mask_r = cv2.erode(mask_r, None, iterations=1)
        mask_r = cv2.dilate(mask_r, None, iterations=3)
        #mask_b = cv2.erode(mask_b, None, iterations=1)
        mask_b = cv2.dilate(mask_b, None, iterations=3)
        
        res_r = cv2.bitwise_and(Gaussianframe,Gaussianframe, mask =mask_r)
        res_b = cv2.bitwise_and(Gaussianframe,Gaussianframe, mask =mask_b)
        
        cnts = cv2.findContours(mask_r, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        hull = [cv2.convexHull(cnt) for cnt in cnts]
        cv2.polylines(Gaussianframe,hull,True,(0,0,255))
        
        center = None
        
        for c in hull:
            if len(c) > 3:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                
                M = cv2.moments(c)
                if not(M["m00"] == 0):
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if cv2.contourArea(c) > 20 and radius > 60:
                    obj.append((x,y))
                    cv2.circle(Gaussianframe, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(Gaussianframe, center, 1, (0, 0, 255), -1)
        
        cnts = cv2.findContours(mask_b, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
            
        hull = [cv2.convexHull(cnt) for cnt in cnts]
        cv2.polylines(Gaussianframe,hull,True,(0,0,255))
        
        center = None
        
        for c in hull:
            if len(c) > 3:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                
                M = cv2.moments(c)
                if not(M["m00"] == 0):
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if cv2.contourArea(c) > 20 and radius > 60:
                    obj.append((x,y))
                    cv2.circle(Gaussianframe, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                    cv2.circle(Gaussianframe, center, 1, (0, 0, 255), -1)
                    target_center = center
        
        object_count = len(obj)
        
        aws_upload+=1
        if aws_upload % 30 == 0:
            #print "trying to push to bucket..."
            pushToBucket()
            aws_upload = 0
        cv2.imshow('image-r', res_r)
        cv2.imshow('image-b', res_b)
        cv2.imshow('blobs', Gaussianframe)
        #time.sleep(.1)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            print "Quitting...!"
            break
    else:
        print "not entering loop..."
        time.sleep(.25)
        
cam.release()
cv2.destroyAllWindows()

print "Closed."