#!/usr/bin/env python

import sys
import time
import getopt
import random
import urllib2
import os.path
import re
import sqlite3 as lite

db_filename = 'craigslist.db'
dump_dir = 'data'
shallow = True

#cities = [ 'sfbay' ]
#sections = [ 'sof' ]

cities = [ 'sfbay', 'washingtondc', 'atlanta', 'portland', 'denver', 
           'boulder', 'seattle', 'raleigh', 'boston', 'newyork' ]
sections = [ 'sof', 'sad' ]

#------------------------------------------------------------------------------
def MakeRSSURL(city, section, page):
    return 'https://'+city+'.craigslist.org/search/'+section+'?format=rss&s='+str(page)

#------------------------------------------------------------------------------
def MakeTag(city, section, id):
    return city+"/"+section+"/"+str(id)

#------------------------------------------------------------------------------
def MakeFileName(city, section, id):
    dir = dump_dir+"/"+city+"/"+section
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir+"/"+str(id)+".html"

#------------------------------------------------------------------------------
def DB_Open():
    needs_table = not os.path.isfile(db_filename)
    try:
        con = lite.connect(db_filename)

        if needs_table:
            with con:
                cur = con.cursor()
                cur.execute("CREATE TABLE status(id STRING, city STRING, section STRING, first_seen DATE, last_seen DATE)")

    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    return con

#------------------------------------------------------------------------------    
def DB_HaveSeenTag(con, tag):
    with con:
        cur = con.cursor()
        cur.execute("SELECT id FROM status WHERE id=:Id", {"Id":tag})
        item = cur.fetchone()
        return item!=None

#------------------------------------------------------------------------------
def DB_Update(con, is_new, tag, city, section):

    with con:
        cur = con.cursor()
        if is_new:
            cur.execute("INSERT INTO status "
                        "  (id,city,section,first_seen,last_seen) "
                        "  VALUES (:Id,:City,:Section,date('now'),date('now'))", 
                        {"Id":tag, "City":city, "Section":section})
        else:
            cur.execute("UPDATE status "
                        "  SET last_seen=date('now') "
                        "  WHERE id=:Id", 
                        {"Id":tag})
    con.commit()


def ExtractLinksFromRSS(page_data):

    links = []
    for line in page_data.split('\n'):
        if line.find("<link>") > -1:
            r = re.compile('<link>(.*?)</link>')
            m = r.search(line)
            link = m.group(1)
            if(link.startswith("http:")):
               links.append(link)
    
    return links


#with open ("sof2.xml", "r") as myfile:
#    data=myfile.read() #.replace('\n', '')
#links = ExtractLinksFromRSS(data)

#rss_url ="https://sfbay.craigslist.org/search/sad?format=rss"
#rss_page = urllib2.urlopen(rss_url).read()
#links = ExtractLinksFromRSS(rss_page)
#for i in links:
#    print i
#print "size +"+str(len(links))
#sys.exit(0)

user_cities = []
try:
    opts,args = getopt.getopt(sys.argv[1:], "dc:", ["deep","city="])
except getopt.GetoptError:
    sys.exit(2)
for opt,arg in opts:
    if opt in ("-d", "--deep"):
        shallow=False
    if opt in ("-c", "--city"):
        user_cities.append(arg)

print "shallow "+str(shallow)
if len(user_cities)>0:
    cities = user_cities
else:
    random.shuffle(cities)


#==============================================================================
con = DB_Open()

#with open ("sof1.txt", "r") as myfile:
#    data=myfile.read().replace('\n', '')

for city in cities:
    for section in sections:

        page=0
        seen_in_page=25
        while (seen_in_page>0):

            rss_url = MakeRSSURL(city, section, page)
            print "Grabbing rss url: "+rss_url
            rss_page = urllib2.urlopen(rss_url).read()
                        
            items = ExtractLinksFromRSS(rss_page)

            seen_in_page = len(items)
            print "Number links seen in page: "+str(seen_in_page)
            #print items

            num_new_links=0
            for item in items:  
                link = item

                b = link.rfind("/")+1
                e = link.rfind(".")
                item_num = link[b:e]

                tag   = MakeTag(city, section, item_num)
                fname = MakeFileName(city, section, item_num)

                is_new = not DB_HaveSeenTag(con, tag)

                print "Grab item: "+item_num+" tag: '"+tag+"' fname: '"+fname+"'" 

                if is_new:                    
                    u = urllib2.urlopen(link)
                    f = open(fname, 'wb') 
                    f.write(u.read())
                    f.close()
                    time.sleep(1)
                    num_new_links=num_new_links+1

                DB_Update(con, is_new, tag, city, section)
                
            #Cut things off if in shallow mode and no new data
            if (shallow) and (num_new_links<5):
                seen_in_page=0

            page=page+seen_in_page

#with open ("doc1.html", "r") as myfile:
#    data=myfile.read().replace('\n', '')
#soup = BeautifulSoup(data,"html.parser")
#text = soup.get_text()

con.close()
