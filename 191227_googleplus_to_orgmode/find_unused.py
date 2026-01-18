import os
import sys
import json
import html.parser as htmlparser
import html2text
import shutil
import urllib.request
import PIL
from pathlib import Path

def IsMentioned(src, f):
    if f in src:
        return True
    else:
        return False
       

    

SRC_DIR="data"
content = open("gplus.org",'r').read()



for file in Path(SRC_DIR).glob('**/*'):
    #print(files)
    f=str(file)
    if os.path.isdir(f):
        continue

    if IsMentioned(content,f):
        #print("FOUND:  ",f)
        continue
   
    
    if not (f.lower().endswith("_sm.jpg") or f.lower().endswith("_sm.png")):
        f2=f.replace(".","_sm.")
        if IsMentioned(content,f2):
            #print("FOUND2: ",f2," ",f)
            continue
                
    print("Miss:   ",f)
    os.rename(f, "data_removed/"+f)
    

#files = os.walk(SRC_DIR)

#files = os.listdir(SRC_DIR)
#for f in files:
#    print(f)
