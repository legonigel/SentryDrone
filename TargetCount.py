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

def pushToBucket(count):
    c = boto.connect_s3()
    b = c.get_bucket('cokecount')
    k = Key(b)
    k.key = 'count'
    
    k.set_contents_from_string(str(count))
    
    print k.get_contents_as_string()
    
    
cv2.namedWindow('image')

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

pts = deque(maxlen=args["buffer"])

# cap = cv2.VideoCapture("./out.mp4")
# while not cap.isOpened():
#     cap = cv2.VideoCapture("./out.mp4")
#     cv2.waitKey(1000)
#     print "Wait for the header"
     
cap = cv2.VideoCapture(0)
 
ret, prev = cap.read()
prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
show_hsv = False
show_glitch = False
cur_glitch = prev.copy()

while(1):
    obj = []
    
    ret, frame = cap.read()
    
    #frame = cv2.imread("./img.png")
    #frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    
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
            
    pushToBucket(len(obj))
    cv2.imshow('image', res)
    cv2.imshow('blobs', Gaussianframe)
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()