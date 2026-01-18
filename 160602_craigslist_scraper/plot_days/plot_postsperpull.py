import math

from matplotlib.dates import strpdate2num, num2date

from pylab import * # matplotlib
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# couldn't remembr enough sql, so rigged it together
# sqlite:
#   select city, first_seen from status order by city,first_seen
# then:
#   uniq -c foo | awk '{print $2 "|"$1}' | sed -e 's/|/\t/g' >pulls_per_date.csv


# Hack to get axis to use a nicer format (12345 => 12,345 
def fmt_commas(val, pos=None):
    s = '%d' % val
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))



line_width=8.0

colors = {
    'boulder':'blue',
    'newyork' : 'darkblue',
    'boston':'purple',
    'washingtondc': 'darkgrey',
    'denver' : 'green',
    'sfbay' : 'red',
    'raleigh':'dimgray',
    'atlanta':'yellow',
    'seattle':'brown',
    'portland':'orange'
}


dt = dtype({'names'   : ['city', 'date', 'count'],
            'formats' : ['S100', int, int]})

city,dates,counts = loadtxt('pulls_per_date.csv', 
                           dtype=dt,
                           converters={1:mdates.strpdate2num('%Y-%m-%d')}, 
                           unpack=True,
                           comments = '#');


#cities=set(city)
#print cities

#for c in ['atlanta']: 
##    #fig,ax=plt.subplots()
#    tt=(city==c)
#    #plt.plot_date(date[tt],counts[tt],'-')
#    m,s,b=plt.stem(dates[tt],counts[tt], markerfmt=" ")
#    plt.setp(s,'color','blue','linewidth',2)
#    plt.gcf().autofmt_xdate() #Makes the dates fit, turns at angle
#    plt.gca().xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%b %Y') )
#plt.show()

cities=[ 'sfbay', 'seattle', 'newyork',  'boston',  'washingtondc', 
         'portland','denver', 'raleigh', 'atlanta','boulder']

# Make below axis dummy plots for all items in order we want for legend
for c in reversed(cities):
    d=dates[0]
    plt.plot( [d,d], [-10,-10], color=colors[c], linewidth=line_width, label=c)

max_val=0
udates=set(dates)
legend_kludge=set()
for d in udates:
    n1=0;
    tt_d = (dates==d)
    for c in cities:
        tt = (city==c) * tt_d
        if tt.any():
            n2 = n1 + counts[tt]
            plt.plot( [d,d], [n1,n2], color=colors[c], linewidth=line_width)
            n1=n2
    max_val=max(max_val, n2)

plt.xlabel('Date')
plt.ylabel('Posts Grabbed')

ax = plt.gca()
ax.set_ylim(0, max_val+100)
ax.xaxis.set_major_formatter( matplotlib.dates.DateFormatter('%b %Y') )
ax.yaxis.set_major_formatter(FuncFormatter(fmt_commas))
#ax.autofmt_xdate() #Makes the dates fit, turns at angle

box = ax.get_position();
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

plt.legend(loc='center left', bbox_to_anchor=(1,0.5))

plt.show()
