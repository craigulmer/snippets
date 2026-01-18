import os
import sys
import json
import html.parser as htmlparser
import html2text
import shutil
import urllib.request
import PIL
from PIL import Image

from pathlib import Path

def IsMentioned(src, f):
    if f in src:
        return True
    else:
        return False
       

    

SRC_DIR="data"
content = open("gplus.org",'r').read()

max_width=1920

for file in Path(SRC_DIR).glob('**/*'):
    #print(files)
    f=str(file)
    if os.path.isdir(f):
        continue

    if (f.lower().endswith("_sm.jpg") or f.lower().endswith("_sm.png") or f.endswith(".orig")):
        continue


    if not (f.lower().endswith(".jpg") or f.lower().endswith(".png")):
        print("Not looking at ",f)
        continue
    
    img = Image.open(f)
    if img.size[0] <= max_width:
        print("Not scaling ",f," width=",img.size[0])
        continue

    f_full_size = f+".orig"
    os.rename(f, f_full_size)

    img = Image.open(f_full_size)
    wpercent = (max_width / float(img.size[0]))
    vsize = int( float(img.size[1]) * float(wpercent))
    print("Scaling ",f," by ",wpercent," to 1920x",vsize)
    img = img.resize((max_width, vsize), PIL.Image.ANTIALIAS)
    img.save(f)
    
