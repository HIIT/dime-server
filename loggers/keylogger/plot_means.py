#!/usr/bin/python3

import sys

import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) < 3:
    print("Error: At least two arguments expected")
    sys.exit()

upper = np.load(sys.argv[1])
lower = np.load(sys.argv[2])

fig, (ax0, ax1) = plt.subplots(nrows=2)

ax0.plot(upper, linewidth=3, label='current')
ax0.set_title('documents')
ax0.axis([0, 50, 0, 0.7])
ax0.grid(True)

ax1.plot(lower, linewidth=3, label='current')
ax1.set_title('keywords')
ax1.axis([0, 50, 0, 0.25])
ax1.grid(True)

if len(sys.argv) == 5:
    upper_old = np.load(sys.argv[3])
    lower_old = np.load(sys.argv[4])
    ax0.plot(upper_old, linewidth=3, label='previous')
    ax1.plot(lower_old, linewidth=3, label='previous')

ax0.legend()
ax1.legend()

plt.savefig('foo.png')
plt.show()
