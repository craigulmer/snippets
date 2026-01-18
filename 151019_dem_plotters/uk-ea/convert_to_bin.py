import sys
import os.path
import getopt

import numpy as np
import matplotlib.pyplot as plt


def convertFileToNumpy(idir,ifile,odir):

    print("Working on "+ifile)

    ifname = idir+"/"+ifile
    ofname = odir+"/"+ifile+".npy"


    data=open(ifname).read()
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

    np.save(ofname, arr)



idir_name = 'data_2m'
odir_name = 'data_bin'

color_map = 'gray' #note: reverse grey is gray_r
try:
    opts,args = getopt.getopt(sys.argv[1:], "i:o:", ["input=","output="])
except getopt.GetoptError:
    sys.exit(2)
for opt,arg in opts:
    if opt in ("-i", "--input"):
        idir_name=arg
    if opt in ("-o", "--output"):
        odir_name=arg

if idir_name == odir_name:
    print("Input and Output directories are the same. Must be different")
    exit(-1)

if not os.path.exists(odir_name):
        os.makedirs(odir_name)


# Walk through directory, plot each file
for dirName, subdirList, fileList in os.walk(idir_name):
    for fname in fileList:        
        convertFileToNumpy(dirName,fname,odir_name)
