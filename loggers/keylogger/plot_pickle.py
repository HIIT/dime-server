#!/opt/local/bin/python2.7

import sys

import pickle
import numpy as np
import matplotlib.pyplot as plt

for a in sys.argv[1:]:
    print a 
    f = open(a) 
    x = pickle.load(f)
    y = np.array(x)
    plt.plot(y[:,0])

plt.show()
