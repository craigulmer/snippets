import sys
import os.path
import getopt

import numpy as np
import matplotlib.pyplot as plt


def plotFile(fname,color_map):
    print fname
    data=open(fname).read()
    lines = data.split('\n')

    # Parse out the number of rows and columns from the header
    ncols = int(lines[0].split()[1])
    nrows = int(lines[1].split()[1])

    # Yuck. Convert each line to an array, then append to a matrix
    arr=np.array([])
    for s in lines[6:]:
        x = np.array(map(float,s.split()))
        arr = np.append(arr, x)
    
    #Convert matrix into the desired shape
    arr = arr.reshape(nrows,ncols)

    #Clamp invalid values to zero
    m=arr.max()
    arr = np.clip(arr,0,m)    
    print arr.max()

    plt.figure()
    plt.imshow(arr,cmap=color_map)
    plt.title(fname)
    plt.show()




dir_name = 'data_2m'
color_map = 'gray' #note: reverse grey is gray_r
try:
    opts,args = getopt.getopt(sys.argv[1:], "d:c:", ["dir=","color="])
except getopt.GetoptError:
    sys.exit(2)
for opt,arg in opts:
    if opt in ("-d", "--dir"):
        dir_name=arg
    if opt in ("-c", "--color="):
        color_map=arg


# Walk through directory, plot each file
for dirName, subdirList, fileList in os.walk(dir_name):
    for fname in fileList:        
        plotFile(dirName+'/'+fname, color_map)
