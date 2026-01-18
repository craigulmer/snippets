from math import *
from random import *
import numpy as np
import xml.etree.ElementTree as et
import sys, getopt, time

import pytz
from datetime import *
from dateutil import parser


ZULU_FMT="%Y-%m-%dT%H:%M:%SZ"
KML_URL="http://earth.google.com/kml/2.2"

def parseTimeToUTC(time_string, time_zone):
    src_time = parser.parse(time_string) #"2005-08-09T11:00")

    local = pytz.timezone(time_zone)
    local_dt = local.localize(src_time, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def haversine(p1, p2): #lon1, lat1, lon2, lat2):
    degree_to_rad = float(pi/180.0)

    d_lon = (p2[0] - p1[0]) * degree_to_rad    
    d_lat = (p2[1] - p1[1]) * degree_to_rad

    a=pow(sin(d_lat/2),2) + cos(p1[1] * degree_to_rad) *  cos(p2[1] * degree_to_rad) * pow(sin(d_lon/2),2)
    c=2*atan2(sqrt(a),sqrt(1-a))
    mi = 3956 * c
    return mi

def parseKML(filename):

    tree = et.parse(filename)
    lineStrings = tree.findall('.//{'+KML_URL+'}LineString')

    for attributes in lineStrings:
        for subAttribute in attributes:
            if subAttribute.tag == '{'+KML_URL+'}coordinates':
                points = subAttribute.text.split()
                track=[]
                for p in points:
                    coords=p.split(",")
                    track.append(coords)
                nptrack=np.array(track)
                return nptrack.astype(np.float)

    print "Error: Didn't find a linestring in "+filename
    sys.exit(-3)



def dumpGPX(activity_type, time_plain, utc_dt, track):

    time_zulu = utc_dt.strftime(ZULU_FMT)

    print """<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.1"
  creator="RunKeeper - http://www.runkeeper.com"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
<trk>"""    
    print "  <name><![CDATA["+activity_type +" "+time_plain+"]]></name>"
    print "  <time>"+time_zulu+"</time>"
    print "  <trkseg>"
    for v in track:
        print "    <trkpt lat=\"{0}\" lon=\"{1}\"><time>{2}</time></trkpt>".format(v[1],v[0],v[2])
    print "  </trkseg>"
    print "</trk>"
    print "</gpx>"

def dumpTCX(activity_type, time_plain, utc_dt, track, avg_heart_rate):

    time_zulu = utc_dt.strftime(ZULU_FMT)


    print """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">"""
    print "<Activities>"
    print "  <Activity Sport=\""+activity_type+"\">"
    print "    <Id>"+time_zulu+"</Id>"
    print "      <Lap StartTime=\""+time_zulu+"\">"
    #print "       <TotalTimeSeconds>"+time_seconds+"</TotalTimeSeconds>"
    #print "       <MaximumSpeed>"+max_speed+"</MaximumSpeed>"
    #print "       <Calories></Calories>"
    print "       <Intensity>Active</Intensity>"
    print "       <TriggerMethod>Location</TriggerMethod>"
    print "       <Track>"
    for v in track:
        heart_rate = int(uniform(avg_heart_rate - 5, avg_heart_rate + 5))
        print "      <Trackpoint>"
        print "        <Time>{0}</Time>".format(v[2])
        print "        <Position>"
        print "           <LatitudeDegrees>{0}</LatitudeDegrees>".format(v[1])
        print "           <LongitudeDegrees>{0}</LongitudeDegrees>".format(v[0])
        print "        </Position>"
        print "        <AltitudeMeters>0</AltitudeMeters>"
        print "        <DistanceMeters>0.00000</DistanceMeters>"
        print "        <SensorState>Absent</SensorState>"
        print "        <HeartRateBpm><Value>"+str(heart_rate)+"</Value></HeartRateBpm>"
        print "      </Trackpoint>"
    print "       </Track>"
    print "      </Lap>"
    print "  </Activity>"
    print "</Activities>"
    print "</TrainingCenterDatabase>"

#http://code.google.com/p/garmintrainer/source/browse/src/main/resources/sample.tcx?r=2731327960cd35d1e1be0612082a7060a19cabf7




def genCircle(num_points, origin, radius_mi):
    
    degree_to_rad = float(pi/180.0)
    ang = 360.0/num_points
    
    rad_deg_lon = radius_mi/53.06 #40deg
    rad_deg_lat = radius_mi/68.99 #40deg
    #rad_deg_lon = radius_mi/69.17 #equator
    #rad_deg_lat = radius_mi/68.71 #equator

    v=[]
    for i in range(num_points):        
        pt = (rad_deg_lon*cos(i*ang*degree_to_rad), rad_deg_lat*sin(i*ang*degree_to_rad))
        v.append(pt)
        print i, pt
    #return v

    sum=0
    for i in range(num_points):
        d= haversine(v[(i+1)%num_points],v[i])
        sum=sum+d
        print i,d, sum
    return v
    
def genRandOffset():
    degree_to_rad = float(pi/180.0)
    #return (0.0, 0.0)
    #r = uniform(0.1, 0.1)
    r=0.00003
    a = uniform(0.0, 360.0)
    return ( r*cos(a*degree_to_rad), r*sin(a*degree_to_rad))
    

def templateLLNLLoop():
    return ( (-121.701130,37.68792125),
             (-121.701371,37.68792125),
             (-121.701478,37.68778540),
             (-121.701532,37.68758163),
             (-121.701414,37.68746277),
             (-121.701232,37.68741607),
             (-121.701012,37.68745428),
             (-121.700872,37.68759437),
             (-121.700872,37.68774295),
             (-121.700996,37.68787455),
             (-121.701092,37.68791276))

# Visit http://bikeroutetoaster.com/BRTWebUI to make more. Export to kml and pull out
# Visit http://www.gpsvisualizer.com/ to view the routes

def createTrackFromTemplateDistanced(template_verts, target_miles, mph, start_time):
    
    current_time=start_time
    results=[];
    total_miles=0
    time=0;
    i=1
    s1 = template_verts[0]
    while(total_miles < target_miles):
        jiggle = genRandOffset()
        s2 = np.add(template_verts[i], jiggle)
        d = haversine(s2,s1)
        
        mph_mod = uniform(mph-2.0, mph+2.0)
        seconds = (d / mph_mod)*3600.0
        current_time = current_time + timedelta(seconds=seconds)

        actual_mph = d/(seconds/3600.0)
        ts=current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        result = (s2[0], s2[1], ts)
        results.append(result)

        #print "Distance ",d,x,s2, seconds, actual_mph,ts
        #print "Distance ",d, "Sec: ", seconds, "MPH: ",actual_mph,ts
        total_miles = total_miles + d
        s1=s2
        i=(i+1)%len(template_verts)

    return results

def createTrackFromTemplateTimed(template_verts, target_seconds, mph, start_time):
    
    current_time=start_time
    results=[];
    total_miles=0
    total_seconds=0
    time=0;
    i=1
    s1 = template_verts[0]
    while(total_seconds < target_seconds):
        jiggle = genRandOffset()
        s2 = np.add(template_verts[i], jiggle)
        d = haversine(s2,s1)
        
        mph_mod = uniform(mph-2.0, mph+2.0)
        seconds = (d / mph_mod)*3600.0
        current_time = current_time + timedelta(seconds=seconds)
        
        actual_mph = d/(seconds/3600.0)
        ts=current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        result = (s2[0], s2[1], ts)
        results.append(result)

        #print "Distance ",d,x,s2, seconds, actual_mph,ts
        #print "Distance ",d, "Sec: ", seconds, "MPH: ",actual_mph,ts
        total_miles = total_miles + d
        total_seconds = total_seconds + seconds
        s1=s2
        i=(i+1)%len(template_verts)

    return results
        

#llnl_loop=(-121.7026296, 37.6875535)
#v=genCircle(10, (0,45), 0.1)
#template_verts = templateLLNLLoop()
#template_verts = templateGiants()
#template_verts = templateBigHouse()

def dumpHelp():
    print "runfaker.py <options>"
    print "  -i input_template.kml  : kml file to use as a template for track"
    print "  -o output.gpx          : output filename for gpx track"
    print "  -d date                : starting date for track (2014-10-26T11:00)"
    print "  -m minutes             : how many minutes the track should go on for"
    print "  -s mph_speed           : how fast you should go"
    sys.exit(2)

def main(argv):

    template_filename=""
    output_filename=""
    time_string="" #2014-10-26T11:00"
    target_mph=8
    target_seconds=30*60
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:m:s:",["ifile=","ofile=","date=","-minutes","-speed"])
    except getopt.GetoptError:
        dumpHelp()

    for opt, arg in opts:
        if opt== "-h":
            dumpHelp()
        elif opt in ("-i", "--ifile"):
            template_filename = arg
        elif opt in ("-o", "--ofile"):
            output_filename = arg            
        elif opt in ("-d", "--date"):
            time_string = arg
        elif opt in ("-m", "--minutes"):
            target_seconds = int(arg)*60
        elif opt in ("-s", "--speed"):
            target_mph = int(arg)
            
    if template_filename=="":
        template_verts = templateLLNLLoop()
    else:
        template_verts = parseKML(template_filename)
        
    if time_string=="":
        time_string=time.strftime("%Y-%m-%dT%H:00")


    utc_dt = parseTimeToUTC(time_string, "America/Los_Angeles")
    #track = createTrackFromTemplateDistanced(template_verts,8,8,utc_dt)
    track = createTrackFromTemplateTimed(template_verts,target_seconds,target_mph,utc_dt)

    # Redirect output to a file if provided with one
    if output_filename != "":
        sys.stdout = open(output_filename,'w')


    #dumpGPX("running", time_string, utc_dt, track)
    dumpTCX("running", time_string, utc_dt, track, 143)


#print track



if __name__ == "__main__":
    main(sys.argv[1:])
