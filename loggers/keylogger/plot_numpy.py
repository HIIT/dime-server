#!/opt/local/bin/python2.7

import sys

import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)<2:
    sys.exit()
for a in sys.argv[1:]:
    x = np.load(a)
    plt.plot(x)
plt.show()
