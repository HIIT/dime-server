#from math_utils import *
import numpy as np
import json

import matplotlib.pyplot as plt

import sys

import os

mvn_avg_n = int(sys.argv[1])
#
#mvn_avg_n = 20
#
#frac_thres = 5.0
frac_thres = float(sys.argv[2])

data_dir = sys.argv[3]


#
filelocatorvec = np.load(data_dir+'/filelocatorlist.npy')

#
# if os.path.isfile(data_dir+"/cossim_vsum_vec.npy"):
#     cossim_vsum_vec = np.load(data_dir+'/cossim_vsum_vec.npy')
if os.path.isfile(data_dir+"/eucl_dist_w_hat_vec.npy"):
    cossim_vsum_vec = np.load(data_dir+'/eucl_dist_w_hat_vec.npy')
#if os.path.isfile(data_dir+"/norm_sigma_hat.npy"):
#    cossim_vsum_vec = np.load(data_dir+'/norm_sigma_hat.npy')


mvng_avg_list = []
removing_locator_list = []
for i in range(len(cossim_vsum_vec)):

    subvec   = cossim_vsum_vec[:(i+1)]

    latest_cossim = subvec[-1:][0]
    mvng_avg = subvec[-(mvn_avg_n+1):-1].mean()
    mvng_avg_list.append(mvng_avg)
    print(latest_cossim)
    print(mvng_avg)

    if (mvng_avg) > 0.0:
    #frac      = (1.0-latest_cossim)/(1.0-mvng_avg)
        if latest_cossim > mvng_avg:
            frac = (latest_cossim)/(mvng_avg)
        else:
            frac = (2*mvng_avg-latest_cossim)/(mvng_avg)
    else:
        frac = 0.0
    #print(frac)
    if frac > frac_thres:
        removing_locator_list.append(1)
    else:
        removing_locator_list.append(0)

removing_locator_vec = np.array(removing_locator_list)
print(removing_locator_vec)
np.save(data_dir+'/removing_locator_vec.npy',removing_locator_vec)


plt.plot(cossim_vsum_vec)
plt.plot(removing_locator_vec)
plt.plot(filelocatorvec)
plt.plot(mvng_avg_list)
plt.show()
