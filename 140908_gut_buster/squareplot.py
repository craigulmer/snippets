# Simple plotter for Gut books. 
# All this does is draw a sqare for every stat in the input
# and color it based on the score. 
#
# Another fine example of how Viz lies to you. You will
# need to fudge the range by adjusting the clipping. 

import numpy as np
import matplotlib.pyplot as plt
import sys as sys

if len(sys.argv) <2:
    print "Need an input file with many rows of 'id score'\n"
    sys.exit(1)

fname = sys.argv[1]

vals = np.loadtxt(fname)

ids = vals[:,0]
score = vals[:,1]

score_max = 400; #max(score)
#score_max = max(score)
score = np.clip(score, 10, score_max)
score = score/score_max
# want 3x1 ratio, so 3n*n= 30824 (max entries),  horiz=3n=300
NUM_COLS=300

fig = plt.figure(figsize=(12,9))
ax = fig.add_subplot(111)
ax.set_axis_bgcolor('0.50')
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

for i in range(len(vals)):
    #print i, ids[i]
    row = int(ids[i]) / NUM_COLS
    col = int(ids[i]) % NUM_COLS
    cval = score[i] #score[i]*score[i]  # Square the values to drop the lower end
    
    cmap = plt.get_cmap('hot')
    val = cmap(cval)
    
    ax.add_patch(plt.Rectangle((col,row),1,1,color=val)); #, cmap=plt.cm.autumn))
    
    ax.set_aspect('equal')

print cmap(0.1)
print cmap(0.9)

plt.xlim([0,NUM_COLS])
plt.ylim([0,1+int(max(ids))/NUM_COLS])
plt.show()
