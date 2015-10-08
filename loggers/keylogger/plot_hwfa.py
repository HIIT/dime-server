#!/usr/bin/python3

import sys

import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) not in [7, 11]:
    print("Error: Either 6 or 10 arguments expected")
    sys.exit()

upper_oracle = np.load(sys.argv[1])
lower_oracle = np.load(sys.argv[2])

upper_cont_cur = np.load(sys.argv[3])
lower_cont_cur = np.load(sys.argv[4])

upper_cont_old = np.load(sys.argv[5])
lower_cont_old = np.load(sys.argv[6])

fig, (ax0, ax1) = plt.subplots(nrows=2)

ax0.plot(upper_oracle, linewidth=3, label='oracle')
ax0.set_title('documents')
#ax0.axis([0, 50, 0, 0.7])
ax0.grid(True)

ax1.plot(lower_oracle, linewidth=3, label='oracle')
ax1.set_title('keywords')
#ax1.axis([0, 50, 0, 0.25])
ax1.grid(True)

#ax0.legend(bbox_to_anchor=(1.1, 1.1))
##ax1.legend(bbox_to_anchor=(1.1, 1.1))
#plt.savefig('foo0.png')
#plt.show()
#sys.exit()

ax0.plot(upper_cont_cur, linewidth=3, label='cont-cur')
ax1.plot(lower_cont_cur, linewidth=3, label='cont-cur')
ax0.plot(upper_cont_old, linewidth=3, label='cont-old')
ax1.plot(lower_cont_old, linewidth=3, label='cont-old')

# ax0.legend(bbox_to_anchor=(1.1, 1.1))
# #ax1.legend(bbox_to_anchor=(1.1, 1.1))
# plt.savefig('foo1.png')
# plt.show()
# sys.exit()

if len(sys.argv) > 7:

    upper_exp_cur = np.load(sys.argv[7])
    lower_exp_cur = np.load(sys.argv[8])
    
    upper_exp_old = np.load(sys.argv[9])
    lower_exp_old = np.load(sys.argv[10])

    ax0.plot(upper_exp_cur, linewidth=3, label='exp-cur')
    ax1.plot(lower_exp_cur, linewidth=3, label='exp-cur')
    ax0.plot(upper_exp_old, linewidth=3, label='exp-old')
    ax1.plot(lower_exp_old, linewidth=3, label='exp-old')

ax0.legend(bbox_to_anchor=(1.1, 1.1))
#ax1.legend(bbox_to_anchor=(1.1, 1.1))
plt.savefig('foo2.png')
plt.show()
sys.exit()
