import math

from pylab import * # matplotlib
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# From sqlite on db:
#   .output num_days_on_list.csv
#   select julianday(last_seen)-julianday(first_seen) from status ;


x = loadtxt('num_days_on_list.csv',usecols=[0], unpack=True, comments = '#');

n, bins, patches = plt.hist(x, 30, normed=0, facecolor='green', alpha=0.75)

#plt.gca().set_ylim(0,max(n)*1.05)

plt.yscale('log', nonposy='clip')
plt.gca().set_ylim(0.5, max(n))
#plt.gca().grid(True, which="majorminor", ls="-")

#plt.gca().set_ylim(-100, max(n))
#plt.gca().set_xlim(-5, max(x)+5)


plt.ylabel("Number of Posts")
plt.xlabel('Days on Craigslist')

print max(x)
plt.show()


