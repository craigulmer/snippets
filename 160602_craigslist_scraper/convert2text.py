import html2text
import string
import os

SRC_DIR = 'data'
DST_DIR = 'text'

def parseHTML(filename):
    html = open(filename).read()
    html = filter(lambda x: x in string.printable, html)
    txt = html2text.html2text(html)

    results=[]
    count=0
    lines = txt.split('\n')
    for i in range(len(lines)):
        if lines[i].startswith('##'):
            count=count+1
        if lines[i].startswith("  * Principals only."):
            break
    
        if count==2:
            results.append(lines[i])
        
        if lines[i].startswith("post id:"):
            break

    
    return '\n'.join(results)


for src_dir, subdirList, fileList in os.walk(SRC_DIR):
    
    dst_dir = DST_DIR + src_dir.lstrip(SRC_DIR)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    print('Found dir %s - %s' % (src_dir, dst_dir))

    for src_name in fileList:
        dst_name = src_name[:-4]+"txt"
        dst_full = dst_dir+"/"+dst_name
        if not os.path.exists(dst_full):
            print "Converting "+dst_full

            txt = parseHTML(src_dir+"/"+src_name)
            txt = filter(lambda x: x in string.printable, txt)

            target = open(dst_full,'w')
            target.truncate()
            target.write(txt)
            target.close()

        else:
            print "Already have "+dst_full

#x= parseHTML('data/atlanta/sof/5180401068.html')
#print x
