#!/usr/bin/python3

import sys

import numpy as np
import matplotlib.pyplot as plt

#if len(sys.argv) not in [7, 11]:
#    print("Error: Either 6 or 10 arguments expected")
#    sys.exit()

upper_baseline = np.load(sys.argv[1])
lower_baseline = np.load(sys.argv[2])

#upper_click0 = np.load(sys.argv[3])
#upper_click1 = np.load(sys.argv[4])
#upper_click2 = np.load(sys.argv[5])
#upper_click3 = np.load(sys.argv[6])

plt.rc('font', family='Times New Roman')

fig, (ax0, ax1) = plt.subplots(nrows=2)
fig.set_size_inches(3.5, 4)

ax0.plot(np.arange(1,51), upper_baseline, linewidth=2, label='baseline')
ax0.yaxis.set_ticks(np.arange(0.2, 1.1, 0.2))
ax0.set_title('document precision')
ax0.axis([0, 50, 0.2, 1.0])
ax0.grid(True)

ax1.plot(np.arange(1,51), lower_baseline, linewidth=2, label='baseline')
ax1.yaxis.set_ticks(np.arange(0, 0.55, 0.1))
ax1.set_title('keyword relevance')
ax1.axis([0, 50, 0, 0.5])
ax1.grid(True)

#ax0.legend(bbox_to_anchor=(1.1, 1.1))
##ax1.legend(bbox_to_anchor=(1.1, 1.1))
#plt.savefig('foo0.png')
#plt.show()
#sys.exit()

#ax0.plot(np.arange(10,21), upper_click0[ 9:20], linewidth=3, label='cont-cur')
#ax0.plot(np.arange(20,31), upper_click1[19:30], linewidth=3, label='cont-old')
#ax0.plot(np.arange(30,41), upper_click2[29:40], linewidth=3, label='cont-old')
#ax0.plot(np.arange(40,51), upper_click3[39:50], linewidth=3, label='cont-old')

# ax0.legend(bbox_to_anchor=(1.1, 1.1))
# #ax1.legend(bbox_to_anchor=(1.1, 1.1))
# plt.savefig('foo1.png')
# plt.show()
# sys.exit()

# if len(sys.argv) > 7:

#     upper_exp_cur = np.load(sys.argv[7])
#     lower_exp_cur = np.load(sys.argv[8])
    
#     upper_exp_old = np.load(sys.argv[9])
#     lower_exp_old = np.load(sys.argv[10])

#     ax0.plot(upper_exp_cur, linewidth=3, label='exp-cur')
#     ax1.plot(lower_exp_cur, linewidth=3, label='exp-cur')
#     ax0.plot(upper_exp_old, linewidth=3, label='exp-old')
#     ax1.plot(lower_exp_old, linewidth=3, label='exp-old')

#ax0.legend(bbox_to_anchor=(1.1, 1.1))
#ax1.legend(bbox_to_anchor=(1.1, 1.1))

plt.tight_layout()
plt.savefig('foo.pdf')
plt.show()
sys.exit()
