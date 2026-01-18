import os
import sys
import json
import html.parser as htmlparser
import html2text
import shutil
import urllib.request
import PIL
from PIL import Image

posts_dir="./Takeout/Google+ Stream/Posts"
data_dir="./data"
max_width=600

parser = htmlparser.HTMLParser()


def cleanupText(content):
    tmp=html2text.html2text(content)
    tmp=tmp.replace('\n\n',"DOUBLE_LINE")
    tmp=tmp.replace('  \n  \n',"DOUBLE_LINE")   #Not sure why, but definitely there     
    tmp=tmp.replace('\n',' ')
    tmp=tmp.replace("DOUBLE_LINE","\n\n")
    tmp=tmp.replace("**","*")
    return tmp

def checkFile(year, item):
    if 'localFilePath' in item:
        #something tangible we can download
        orig_img=item['localFilePath']
        orig_img = posts_dir+"/"+orig_img
        name=orig_img.split('/')[-1]
        dst_file_caps=data_dir+"/"+year+"/"+name;
        dst_file=data_dir+"/"+year+"/"+name.lower();

        if os.path.isfile(dst_file_caps) and not os.path.isfile(dst_file):
            eprint("RENAME: ",dst_file)
            os.rename(dst_file_caps, dst_file)
            

        if not os.path.isfile(dst_file):

            if os.path.isfile(orig_img):
                eprint("FILE COPY: ",orig_img)
                shutil.copy(orig_img, dst_file)
                
            else:
                if 'url' in item:
                    url=item['url']
                    eprint("FILE MISSING: ", url)
                    try:
                        urllib.request.urlretrieve(url, dst_file)
                    except:
                        eprint("Could not grab '%s' and write to '%s'" % (url,dst_file))
                else:
                    eprint("FILE NoURL: ",orig_img)

                    
        if( os.path.isfile(dst_file) and (dst_file.endswith(".jpg") or dst_file.endswith(".png")) ):
            thumb_file = dst_file[:-4] + "_sm" + dst_file[-4:]
            if not os.path.isfile(thumb_file):
                eprint("Working on ",dst_file)
                img = Image.open(dst_file)
                if img.size[0] > max_width:
                    wpercent = (max_width / float(img.size[0]))
                    hsize = int( float(img.size[1]) * float(wpercent))                    
                    img =  img.resize((max_width, hsize), PIL.Image.ANTIALIAS)

                    if wpercent < 0.51:
                        img.save(thumb_file)
                        eprint("Scaling: %s to %s by %f" % (dst_file, thumb_file, wpercent))
                        dst_file = thumb_file
                    else:
                        # Not big enough, just resize in place
                        os.rename(dst_file, dst_file+".orig")
                        img.save(dst_file)
            else:
                dst_file=thumb_file
                    
        print("[[%s]]" % (dst_file)) #,orig_img))
        
    elif 'url' in item:
        #Could be youtube link
        print("link: [[%s]]" % item['url'])
        

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
def dumpFile(fname):
    with open(fname,"r") as f:
        data=json.load(f)
        
        post_date=data['creationTime'].split(' ')[0]
        year=post_date.split('-')[0]

        if not 'content' in data:
            eprint("MISSING: ",post_date)
            return
                
        #content=parser.unescape(data['content']).replace("<br>","\n")
        #content=content.replace("<b>","**")
        #content=content.replace("</b>","**")

        content=cleanupText(data['content'])
        
        #if "I need to write" in data['content']:
        #    print("ORIGINAL: ",data['content'])
        #    print("PLAIN:    ",content)
        #    print("MODIFIED: ",mcontent)
        #    print("PIDNA:    ",content.encode("punycode"))
        #    sys.exit(0)
        
        print("* <%s> :gplus:" % post_date)
        print(content)

        if 'link' in data:
            link = data['link']
            imageUrl=""
            title=""
            if 'imageUrl' in link:
                imageUrl=link['imageUrl']
            if 'title' in link:
                title=link['title']
            print("\nlink: [[%s][%s]]" % (link['url'],title))

        if 'media' in data:
            media = data['media']
            checkFile(year, media)
            
        if 'album' in data:
            album = data['album']
            if 'media' in album:
                for media in album['media']:
                    checkFile(year, media)

        if 'comments' in data:
            print("** Google+ Comments")
            comments = data['comments']
            for comment in comments:
                if ('author' in comment) and ('content' in comment):
                    author=comment['author']['displayName']
                    line=cleanupText(comment['content'])
                    print("*%s*: %s" % (author,line))
            
                


files = os.listdir(posts_dir)
files.sort(reverse=True)
for file in files:
    current = os.path.join(posts_dir, file)
    dumpFile(current)
