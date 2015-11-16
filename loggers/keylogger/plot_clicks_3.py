#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import sys

#How many elements to plot from each data vector?

if len(sys.argv) < 2:
    print("Error: At least one file expected")
    sys.exit()

#Load several numpy files containing single vector
vectors = []
filenames = []
#
for i in range(len(sys.argv)):

	#
	if i==0:
		continue

	#
	filename = sys.argv[i]
	filenames.append(filename)
	print(filename)
	vector = np.load(filename)
	vector = vector.tolist()

	#Trim the vector (i.e. remove the tail of zeros)
	for i in range(len(vector)):
		if vector[-1] == 0.0:
			del vector[-1]

	#
	vectors.append(vector)



#Plot settings
plt.rc('font', family='Times New Roman')
plt.figure(figsize=(7,4)) 
plt.axis([0, 50, 0.05, 0.45])


#List of label strings
labelstrs = []
#List of used plotting colors (i.e. line colors)
used_plot_colors = []
for i in range(len(vectors)):

	# #Take label strings
	# name = filenames[i].split('.')[0]
	# parts = name.split('_')
	# for part in parts:
	# 	if part[0] == 'c':
	# 		labelstr = part
	# 		break
	# 	else: 
	# 		labelstr = ''

	#
	if '/' in filenames[i]:
		name = filenames[i].split('/')[-1]
	else:
		name = filenames[i]
	#
	if '.' in name:
		name = name.split('.')[0]
	#
	if '_' in name:
		parts = name.split('_')

	for part in parts:
		if part[0] == 'c':
			labelstr = part
			break
		else: 
			labelstr = ''


	#Check if the label string does not exist
	if labelstr not in labelstrs:
		#
		print(labelstr)
		#Store the label string
		labelstrs.append(labelstr)
		
		#Plot 
		xvec = range(len(vectors[i][0:]))
		xvec = [x+1 for x in xvec]
		print(len(vectors[i]))
		plot_data_vec = plt.plot(xvec[0:-10], vectors[i][0:-10], linewidth = 4.0, label = labelstr)

		#Get the matplotlib.lines.Line2D -object
		print(type(plot_data_vec[0]))
		for i2,item in enumerate(plot_data_vec):
			#print(type(item))
			if type(item) is matplotlib.lines.Line2D:
				line = item
		#Take and store the corresponding plot color
		used_plot_colors.append(line.get_c())

		#Plot clicks with dashed style
		plt.plot(xvec[-11:], vectors[i][-11:], color=line.get_c(), linewidth = 4.0, linestyle='dashed')

	#If label string already exist, plot the line with using the same correpsponding color 
	else:
		print(len(vectors[i]))
		#Get index of the used label string
		plotind = labelstrs.index(labelstr)
		#Get the corresponding color
		plotcolor = used_plot_colors[plotind]
		#Plot with the corresponding color
		xvec = range(len(vectors[i][0:]))
		xvec = [x+1 for x in xvec]
		plt.plot(xvec[0:-10], vectors[i][0:-10], color = plotcolor, linewidth = 4.0)
		#Plot clicks with dashed style
		plt.plot(xvec[-11:], vectors[i][-11:], color=plotcolor, linewidth = 4.0, linestyle='dashed')		


#Plot legends
#plt.legend(bbox_to_anchor=(1.0, 1), loc=2, borderaxespad=0.)
#plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.legend(loc=4, borderaxespad=0.)

#Plot grid
ax = plt.gca()
ax.grid(True)

#Set title, and x- and y-labels
#ax.set_title('Query including both written words and model input (10 keywords)')
ax.set_title('Query including model input (10 keywords)')
#ax.set_xlabel('Number of written words')
#ax.set_ylabel('Precision@5')

#Plot legends
#
#plt.legend(loc=4)

#Plot title
plt.tight_layout()

plt.show()
