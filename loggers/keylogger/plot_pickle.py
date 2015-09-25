#!/opt/local/bin/python2.7

import sys

import pickle
import numpy as np
import matplotlib.pyplot as plt

means = []
for i in range(0,50):
    means.append([])

for a in sys.argv[1:]:
    print "Processing", a 
    f = open(a) 
    x = pickle.load(f)
    for i,xx in enumerate(x):
        if i<50:
            #print i,xx
            means[i].append(xx[0])
    y = np.array(x)
    plt.plot(y[:,0])

meanvector = np.zeros(50)
for i,m in enumerate(means):
    if len(m):
        #print i, len(m), type(m), m[0]
        meanvector[i] = float(sum(m))/len(m)
plt.plot(meanvector, linewidth=5, color='k')
    
plt.show()
