#!/usr/bin/python3

import sys
import math

import pickle
import numpy as np

import os

if 'DISPLAY' not in os.environ or 'NOPLOT' in os.environ:
    import matplotlib
    matplotlib.use("Agg")

import matplotlib.pyplot as plt

vindex = int(sys.argv[1])

means = []
for i in range(0,50):
    means.append([])

first = True
meanvectorfn = "mean_" + sys.argv[1] +  '_'

parts1 = sys.argv[2].split("/")
parts2 = parts1[0].split("-")
clicking_starts = int(parts2[-2])
print("Clicking starts at", clicking_starts)

for a in sys.argv[3:]:
    print("Processing", a)
    f = open(a, 'rb')
    x = pickle.load(f)
    xmax = 0
    for i,xx in enumerate(x):
        if i>clicking_starts-1 and xx[vindex]>xmax:
            xmax = xx[vindex]
        if i>clicking_starts-1 and xx[vindex]<xmax:
            xx[vindex] = xmax
        if i<50 and not math.isnan(xx[vindex]):
            #print i,xx
            means[i].append(xx[vindex])
    y = np.array(x)
    plt.plot(y[:,vindex])
    if first:
        first = False
        parts = a.split("/")
        meanvectorfn += parts[0]
        if a.find("old") > -1:
            meanvectorfn += "_old"

meanvector = np.zeros(50)
for i,m in enumerate(means):
    if len(m):
        #print i, len(m), type(m), m[0]
        meanvector[i] = float(sum(m))/len(m)

print("Saved", meanvectorfn)
np.save(meanvectorfn, meanvector)

plt.plot(np.arange(1,51), meanvector, linewidth=5, color='k')
plt.savefig('pickle.png')
plt.show()
