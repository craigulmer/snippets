import numpy as np
import cv2
import os


def nothing(x):
    pass

def loadFile(fname):
    x=np.load(fname)
    x = x/x.max()
    (h,w) = x.shape[:2]
    center = (w/2,h/2)
    #return x
    rx = cv2.resize(x, (640,480))# interpolation = cv2.INTER_AREA)
    return rx

def getFilenames(base_dir):
    my_list=[]
    for dirName, subdirList, fileList in os.walk(base_dir):
        for fname in fileList:
            my_list.append(dirName+"/"+fname)
    return my_list



cv2.namedWindow('image')
cv2.createTrackbar('val','image', 0.0, 100.0, nothing)

spot=0
fnames = getFilenames('data_bin_50cm')
rx = loadFile(fnames[spot])
level = 50


print("Slider: change threshold (percent of max value of original")
print("Spacebar: Select next image")
print("Escape: exit")

while(1):
    #print level
    tmp=rx
    tmp=np.clip(tmp, 0,level/100.0) #level-5, level+5)
    cv2.imshow('image',tmp)
    k = cv2.waitKey(1) & 0xFF
    if k==27: #escape
        break
    if k==32: #Spacebar
        spot = spot+1
        rx = loadFile(fnames[spot])

    level = cv2.getTrackbarPos('val','image')

cv2.destroyAllWindows()
