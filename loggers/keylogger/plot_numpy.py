#!/opt/local/bin/python2.7

import sys

import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)==2:
    x = np.load(sys.argv[1])
    plt.plot(x)
    plt.show()
