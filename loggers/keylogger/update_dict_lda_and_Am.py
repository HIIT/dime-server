#!/usr/bin/python
# -*- coding: utf-8 -*-

# For DiMe server queries
import requests
import socket
import json

#For storing lists
import pickle 

#
import sys

#
import numpy as np

#
from scipy import sparse
import scipy.sparse.linalg

#For LDA (Latent dirichlet allocation)
import gensim
from gensim import corpora, models, similarities, interfaces

#For rapid keyword extraction
import rake

#for comparing words 
#Learn tfidf model from the document term matrix
import difflib

#
#import matplotlib.pyplot as plt

#
import os

def read_user_ini():

    f          = open('user.ini','r')
    dumstr     = f.read()
    stringlist = dumstr.split()

    for i in range( len(stringlist) ):
            if stringlist[i] == "server_url:":
                    srvurl = stringlist[i+1]
            if stringlist[i] == "usrname:":
                    usrname = stringlist[i+1]
            if stringlist[i] == "password:":
                    password = stringlist[i+1]
            if stringlist[i] == "time_interval:":
                    time_interval_string = stringlist[i+1]
                    time_interval = float(time_interval_string)
            if stringlist[i] == "nspaces:":
                    nspaces_string = stringlist[i+1]
                    nspaces = int(nspaces_string)
            if stringlist[i] == "numwords:":
                    dum_string = stringlist[i+1]
                    numwords = int(dum_string)                      
            if stringlist[i] == "updating_interval:":
                    dum_string = stringlist[i+1]
                    updateinterval = float(dum_string)  

    return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval


#
def update_all_data():
	
	print "Update data!!"
	srvurl, username, password, time_interval, nspaces, nwords, updateinterval = read_user_ini()

	cpath  = os.getcwd()
	cpathd = cpath + '/' + 'data'	

	if not os.path.isdir(cpathd):
		os.makedirs(cpathd)
	#os.chdir(cpathd)
	#print 'Path: ', os.getcwd()
	#
	update_data(srvurl, username, password)
	update_dictionary()			
	update_doctm(cpathd)
	update_doc_tfidf_list(cpathd)
	update_docsim_model()
	update_Xt_and_docindlist([0])
	update_tfidf_model(cpathd)
	create_stopwordlist(cpathd)	

#Check whether to update data files
def check_update():

	#
	srvurl, username, password, time_interval, nspaces, nwords, updateinterval = read_user_ini()

	#Get current path
	cpath  = os.getcwd()
	cpathd = cpath + '/' + 'data'
	
	#
	if os.path.exists(cpathd):
		print 'Search thread: check_update: data/ folder EXISTS!'
		#os.chdir(cpathd)
		#print 'check_update: ', cpath
		if not os.path.isfile('data/json_data.txt'):
			update_data(srvurl, username, password)

		if not os.path.isfile('/tmp/dictionary.dict'):
			update_dictionary()			

		if not os.path.isfile('data/doctm.data'):
			update_doctm(cpathd)
			update_doc_tfidf_list(cpathd)

		if not os.path.isfile('/tmp/docsim.model'):
			update_docsim_model()

		if not os.path.isfile('data/docindlist.list'):
			update_Xt_and_docindlist([0])

		if not os.path.isfile('data/tfidfmodel.model'):
			update_tfidf_model(cpathd)

		if not os.path.isfile('data/stopwordlist.list'):
			create_stopwordlist(cpathd)
		#Go back in directory
		#os.chdir('../')

		#print 'check_update: ', os.getcwd()
	else: 
		print 'Search thread: check_update: data/ DOES NOT EXISTS! CREATE ONE!'
		#Create data folder into the current path
		os.makedirs(cpathd)
		#os.chdir(cpathd)
		#print 'Path: ', os.getcwd()
		#
		update_data(srvurl, username, password)
		update_dictionary()			
		update_doctm(cpathd)
		update_doc_tfidf_list(cpathd)
		update_docsim_model()
		update_Xt_and_docindlist([0])
		update_tfidf_model(cpathd)
		create_stopwordlist(cpathd)		
		# update_data(srvurl, username, password)
		# update_dictionary()
		# update_doctm()
		# update_doc_tfidf_list()
		# update_docsim_model()
		# update_Xt_and_docindlist([0])
		# update_tfidf_model()
		# create_stopwordlist()

	#print 'Search thread: check_update: ', os.getcwd()	



#Update data
def update_data(srvurl, username, password):
	### IMPORT DATA from DiMe #######	
	print "Importing data from DiMe!!"

	#------------------------------------------------------------------------------

	server_url = str(srvurl)
	server_username = str(username)
	server_password = str(password)

	#------------------------------------------------------------------------------

	# ping server (not needed, but fun to do :-)
	r = requests.post(server_url + '/ping')

	if r.status_code != requests.codes.ok:
		print('No connection to DiMe server!')
		sys.exit(1)

	r = requests.get(server_url + '/data/informationelement',
	                 headers={'content-type': 'application/json'},
	                 auth=(server_username, server_password),
	                 timeout=20)
	 
	dumdata = r.json()
	#
	data = []
	for i in range(len(dumdata)):
		if dumdata[i].has_key('plainTextContent'):
			data.append(dumdata[i])
	
	#
	f = open('data/json_data.txt','w')	
	json.dump(data, f)



# Update dictionary
def update_dictionary():

	print 'Search thread: update_dictionary: current path:', os.getcwd()

	print "Search thread: Updating dictionary!"
	f = open('data/json_data.txt','r')
	data = json.load(f)

	#Create list of documents
	ndocuments = len(data)
	print 'Search thread: num. of docs: ', ndocuments
	documentlist = []
	for i in range(ndocuments):
		#Check that data object (that is now in python dict-form) has key 'plainTextContent'
		if data[i].has_key('plainTextContent'):
			documentlist.append(data[i]['plainTextContent'])


	#####################
	# Update dictionary from words occurring in 'documentlist' ################
	#####################

	# Read list of forbidden words #
	s1 = open('stop-words/stop-words_english_1_en.txt','r')
	s2 = open('stop-words/stop-words_english_2_en.txt','r')
	s3 = open('stop-words/stop-words_english_3_en.txt','r')
	s4 = open('stop-words/stop-words_finnish_1_fi.txt','r')
	s5 = open('stop-words/stop-words_finnish_2_fi.txt','r')
	#
	sstr1=s1.read()
	sstr2=s2.read()
	sstr3=s3.read()
	sstr4=s4.read()
	sstr5=s5.read()

	#
	sstr  = sstr1 + sstr2 + sstr3 + sstr4 + sstr5
	stoplist = set(sstr.split())

	#
	wordlist = []
	#Take all words
	for doc in documentlist:
		#pass
		for word in doc.lower().split():
			#Check if the string consist of alphabetic characters only
			if word.isalpha() and (word not in stoplist):
				wordlist.append(word)

	#Create dictionary
	dictionary = corpora.Dictionary([wordlist])

	#Save dictionary for future use
	dictionary.save('/tmp/tmpdict.dict')
	#dictionaryvalues = dictionary.values()

def create_stopwordlist(destinationfolder):
	print 'Search thread: Create stop word list'

	# Read list of forbidden words #
	s1 = open('stop-words/stop-words_english_1_en.txt','r')
	s2 = open('stop-words/stop-words_english_2_en.txt','r')
	s3 = open('stop-words/stop-words_english_3_en.txt','r')
	s4 = open('stop-words/stop-words_finnish_1_fi.txt','r')
	s5 = open('stop-words/stop-words_finnish_2_fi.txt','r')
	sstr1=s1.read()
	sstr2=s2.read()
	sstr3=s3.read()
	sstr4=s4.read()
	sstr5=s5.read()
	#
	sstr  = sstr1 + sstr2 + sstr3 + sstr4 + sstr5
	#Create list of forbidden words
	stoplist = set(sstr.split())

	f = open(destinationfolder+'/stopwordlist.list','w')
	pickle.dump(stoplist, f)

#Update list of bag of word vectors of documents, denoted by 'doctm'
def update_doctm(destinationfolder):

	print "Updating document term frequency matrix!"

	#Import dictionary
	dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
	nwords = len(dictionary)

	#Import data
	f = open('data/json_data.txt','r')
	data = json.load(f)

	#Create list of documents
	ndocuments = len(data)
	documentlist = []
	for i in range(ndocuments):
		if data[i].has_key('plainTextContent'):
			documentlist.append(data[i]['plainTextContent'])

	#Create document term matrix 'doctm'
	doctm = []
	for i in range(len(documentlist)):
		test_vec_dum = dictionary.doc2bow(documentlist[i].lower().split())
		doctm.append(test_vec_dum)
		#print test_vec_dum

	#Store number of docs
	ndocs = len(doctm)
	varlist = [nwords, ndocs]
	f = open(destinationfolder+'/varlist.list', 'w')
	pickle.dump(varlist, f)
	f.close()

	#Store the data of doctm
	f = open(destinationfolder+'/doctm.data','w')
	pickle.dump(doctm, f)


def update_tfidf_model(destinationfolder):
	#Import doctm
	f = open('data/doctm.data','r')
	doctm = pickle.load(f)

	#Learn tfidf model from the document term matrix
	tfidf = models.TfidfModel(doctm)
	tfidf.save(destinationfolder+'/tfidfmodel.model')


#Updates the tfidf version of doctm (denoted by 'doc_tfidf_list')
#and saves the 'doc_tfidf_list also in sparse matrix form (more specifically in scipy sparse csc_matrix form)
def update_doc_tfidf_list(destinationfolder):

	print "Update doc tfidf list and its corresponding sparse matrix repr.!"

	#Import dictionary
	dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

	f = open('data/doctm.data','r')
	doctm = pickle.load(f)
	#print 'rows doctm', len(doctm)

	#Learn tfidf model from the document term matrix
	tfidf = models.TfidfModel(doctm, normalize = True)

	#Make tfidf-list from doctm using tfidf-model
	doc_tfidf_list = []
	for i in range(len(doctm)):
	    doc_tfidf_dum = tfidf[doctm[i]]
	    doc_tfidf_list.append(doc_tfidf_dum)

	#
	f = open(destinationfolder+'/doc_tfidf_list.data','w')
	pickle.dump(doc_tfidf_list,f)

	#Make also sparse matrix representation of doctm and doc_tfidf_list
	sparsemat = doc_tfidf_list_to_sparsemat(doctm)
	print 'Search thread: doctm sparsemat shape, ', sparsemat.shape
	save_sparse_csc(destinationfolder+'/sXdoctm.sparsemat',sparsemat)

	sparsemat = doc_tfidf_list_to_sparsemat(doc_tfidf_list)
	print 'Search thread: sparsemat shape, ', sparsemat.shape
	save_sparse_csc(destinationfolder+'/sX.sparsemat',sparsemat)


#Converts doc_tfidf_list to scipy sparse matrix format (as csc_matrix)
def doc_tfidf_list_to_sparsemat(doc_tfidf_list):
	#Import dictionary
	dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
	nwords = len(dictionary)

	nrow = len(doc_tfidf_list)
	sparsemat = sparse.lil_matrix((nrow, nwords))
	row = 0
	for d in doc_tfidf_list:
		for c in d:
			sparsemat[row,c[0]] = c[1]
		row = row + 1
	sparsemat = sparsemat.tocsc()

	return sparsemat


#Saves the scipy sparse matrix of form csc_matrix
def save_sparse_csc(filename,array):
    np.savez(filename,data = array.data ,indices=array.indices,
             indptr =array.indptr, shape=array.shape )

#Loads the scipy sparse matrix of form csc_matrix
def load_sparse_csc(filename):
    loader = np.load(filename)
    return sparse.csc_matrix((  loader['data'], loader['indices'], loader['indptr']),
                         shape = loader['shape'])	



def update_Xt_and_docindlist(docindlist):

	#print docindlist 
	#Import X matrix needed in LinRel
	#X = np.load('X.npy')
	if os.path.isfile('data/sX.sparsemat.npz'):
		sX = load_sparse_csc('data/sX.sparsemat.npz')
	else:
		update_doc_tfidf_list()
		sX = load_sparse_csc('data/sX.sparsemat.npz')

	#Save docindlist 
	if os.path.isfile('data/docindlist.list'):
		f = open('data/docindlist.list','r')
		docindlistprev = pickle.load(f)
		#Merge new and old list of indices
		docindlist = list(set(docindlist + docindlistprev))
		docindlist.sort()
		f = open('data/docindlist.list','w')
		#print 'Search thread: Updated docindlist: ', docindlist
		pickle.dump(docindlist,f)
	else:
		#Save docindlist (the list of indices of suggested documents)		
		f = open('data/docindlist.list','w')
		docindlist.sort()
		print 'Search thread: Updated docindlist first time: ', docindlist
		pickle.dump(docindlist,f)

	#Save list of indices of omitted documents 
	if os.path.isfile('data/docindlist.list'):
		docindlisttot = range(sX.shape[0])
		omittedindlist= np.delete(docindlisttot,docindlist,0)
		omittedindlist= omittedindlist.tolist()

		#Save list of omitted docs
		f = open('data/omittedindlist.npy','w')
		pickle.dump(omittedindlist,f)


def doc_tfidf_list_to_array(tfidf_list, nwords):
	ndocuments = len(tfidf_list)	

	tfidf_array = np.zeros((nwords,ndocuments))
	#
	for nvec, tfidf_vec in enumerate(tfidf_list):
	    #print nvec
	    for wi in range(len(tfidf_vec)):
	        wid, score = tfidf_vec[wi]
	        #print wid, score
	        tfidf_array[wid, nvec] = score

	tfidf_array = tfidf_array.transpose()
	#print 'tfidf ', tfidf_array.shape

	#Normalize rows of tfidf_array
	for i in range(tfidf_array.shape[0]):
		dumvec = tfidf_array[i][:]
		sumvec = np.sum(dumvec,axis=0)
		if sumvec > 0.0:
			dumvec = dumvec/float(sumvec)
		tfidf_array[i][:] = dumvec

	return tfidf_array

#Update similarity vector
def update_docsim_model():

	#Import dictionary 
	if os.path.isfile('/tmp/tmpdict.dict'):
		dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
	else:
		#cpath  = os.getcwd()
		#cpathd = cpath + '/' + 'data'
		#os.chdir(cpathd)
		update_dictionary()
		dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
		#os.chdir('../')

	#Import document term matrix
	f = open('data/doctm.data','r')
	doctm = pickle.load(f)

	#Build index
	index = similarities.docsim.Similarity('/tmp/similarityvec',doctm, num_features = len(dictionary), num_best = 20)
	index.num_best = 20
	index.save('/tmp/similarityvec')

#Updates LinRel matrix, denoted by A 
def update_A(docinds, y):

	#Load sparse tfidf matrix
	#sX = np.load('sX.npy')
	sX = load_sparse_csc('data/sX.sparsemat.npz')	

	print "Search thread: Updating A"

	#Compute estimation of weight vector (i.e. user model)
	print 'Search thread: Create Xt '
	sXcsr = sX.tocsr()
	print 'Search thread: Type of sXcsr: ', type(sXcsr)
	sXtcsr= sXcsr[docinds,:]
	Xt    = sXtcsr.toarray()
	print 'Search thread: Xt shape: ', Xt.shape
	print 'Search thread: y shape: ', y.shape

	#
	w = estimate_w(Xt,y)
	w = np.array([w])
	w = w.transpose()
	#test_vec_full = twotuplelist2fulllist(test_vec, nwords)
	#plt.plot(range(len(w)), w)
	#plt.show()

	#
	yT    = y.transpose()
	norm_y= np.linalg.norm(yT)
	if norm_y > 0.0:
		yT  = yT/(norm_y*norm_y)

	#Update A
	Atilde = w*yT
	print 'Search thread: Shape of Atilde: ', Atilde.shape
	print 'Search thread: Max val of Atilde: ', Atilde.max()
	sAtilde= sparse.csc_matrix(Atilde)
	#print 'type sX, ', type(sX), 'shape, ', sX.shape
	#print 'type sAtilde,', type(sAtilde), 'shape, ', sAtilde.shape
	sA = sX*sAtilde
	#A     = np.dot(X,Atilde)

	#np.save('A.npy', A)
	#update_Xt_and_docindlist(docinds)

	return sA






 
#Compute Tikhonov regularized solution for y=Xt*w (using scipy function lsqr)
#I.e. compute estimation of user model
def estimate_w(Xt,y):
	#
	#mu = 1.5
	mu = 0.0
	w = scipy.sparse.linalg.lsqr(Xt,y, damp=mu)[0]
	return w


#Make full array from tfidf_vec (= is a list of 2-tuples i.e. (location, tfidf_value) ) 
def make_tfidf_array(tfidf_vec, dictionary):

    #Number of words in dictionary
    nwords = len(dictionary)

    #Initialize tfidf-vector (numpy-array)
    tfidf_array = np.zeros(nwords)

    for wi in range(len(tfidf_vec)):
        wid, score = tfidf_vec[wi]
        #print "word id " + str(wid) + " word: " + str(dictionary[wid]) + " score:  " + str(score)
        tfidf_array[wid] = score

    return tfidf_array


#
def create_topic_model_and_doctid(numoftopics):

	print "Create topic model!"

	#Import data
	f = open('json_data.txt','r')
	data = json.load(f)

	#Import dictionary
	dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

	#Import document term matrix
	f = open('doctm.data','r')
	doctm = pickle.load(f)

	#Number of documents in database
	ndocuments = len(doctm)

	#Compute cluster distributions (topics)
	#ldamodel = models.LdaModel(doctm, num_topics = numoftopics, id2word = dictionary, passes=10, iterations=200)
	ldamodel = models.LdaModel(doctm, num_topics = numoftopics, id2word = dictionary, passes=10, iterations=20)

	#Save 'ldamodel' for future use
	ldamodel.save('/tmp/tmpldamodel')

    #Compute topic ids for documents
	dtid = []
	for i in range(len(doctm)):
		dumtidv = []
		dumtpv  = []
		doc_lda = ldamodel[doctm[i]]
		for j in range(len(doc_lda)):
			dumtidv.append(doc_lda[j][0])
			dumtpv.append(doc_lda[j][1])
		dtid.append(dumtidv[np.argmax(dumtpv)])
	dtid = np.array(dtid)
	np.save('doctid.npy',dtid)


	#Print words in topics
	# for i in range(numoftopics):
	# 	#Print most probable words in each cluster
	# 	print 'topic ' + str(i)
	# 	prkw = ldamodel.show_topic(i, topn=10)
	# 	for j in range(len(prkw)):
	# 		print prkw[j][0], prkw[j][1]

	
	#Compute doc. ind list of each topic
	topicdocindlist = []
	for i in range(numoftopics):
		#print np.where(dtid == i)[0]
		topicdocindlist.append(np.where(dtid==i)[0])

	#Store the data of doctm
	f = open('topicdocindlist.list','w')
	pickle.dump(topicdocindlist, f)


#
def update_topic_model_and_doctid():

	print "Updating topic model!"

	#Import data
	f = open('json_data.txt','r')
	data = json.load(f)

	#Import dictionary
	dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

	#Import lda model
	ldamodel = models.LdaModel.load('/tmp/tmpldamodel')

	#Import document term matrix
	f = open('doctm.data','r')
	doctm = pickle.load(f)

	#Import topic document index list (for computing the number of topics )
	f = open('topicdocindlist.list','r')
	topicdocindlist = pickle.load(f)
	numoftopics = len(topicdocindlist)

	#Number of documents in database
	ndocuments = len(doctm)

	#Compute cluster distributions (topics)
	#ldamodel = models.LdaModel(doctm, num_topics = numoftopics, id2word = dictionary, passes=10, iterations=200)
	ldamodel.update(doctm)

	#Save 'ldamodel' for future use
	ldamodel.save('/tmp/tmpldamodel')

    #Compute topic ids for documents
	dtid = []
	for i in range(len(doctm)):
		dumtidv = []
		dumtpv  = []
		doc_lda = ldamodel[doctm[i]]
		for j in range(len(doc_lda)):
			dumtidv.append(doc_lda[j][0])
			dumtpv.append(doc_lda[j][1])
		dtid.append(dumtidv[np.argmax(dumtpv)])
	dtid = np.array(dtid)
	np.save('doctid.npy',dtid)

	#Compute doc. ind list of each topic
	topicdocindlist = []
	for i in range(numoftopics):
		#print np.where(dtid == i)[0]
		topicdocindlist.append(np.where(dtid==i)[0])

	#Store the data of doctm
	f = open('topicdocindlist.list','w')
	pickle.dump(topicdocindlist, f)



#######


# #Creates full tfidf numpy array of documents (not recommended)
# def update_X():
# 	#Creates tfidf numpy array

# 	f = open('doc_tfidf_list.data','r')
# 	doc_tfidf_list = pickle.load(f)

# 	#Import dictionary
# 	dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
# 	nwords = len(dictionary)

# 	#Let's simplify notation
# 	#X      = tfidf_array
# 	X      = doc_tfidf_list_to_array(doc_tfidf_list,nwords)
# 	print "X shape, ", X.shape

# 	#Save Xt matrix into a binary NumPy file for further use
# 	np.save('X.npy',X)



# #Updates LinRel matrix
# #(Not recommended)
# def update_A_slow():
# 	print "Updating A"
# 	#
# 	X  = np.load('X.npy')
# 	Xt = np.load('Xt.npy')
# 	XtT= np.transpose(Xt)

# 	#Convert into a scipy sparse matrix
# 	sX  = sparse.csc_matrix(X)
# 	sXt = sparse.csc_matrix(Xt)
# 	sXtT= sparse.csc_matrix(XtT)

# 	print sX.shape
# 	print sXt.shape

# 	#Regularization parameter
# 	mu = 10.5

# 	print "Compute XtTXt"
# 	sXtTXt = sXtT*sXt
# 	print sXtTXt.shape
# 	nr, nc = sXtTXt.shape
# 	print nc
# 	sI   = sparse.identity(nc)
# 	#sI  = sparse.csr_matrix(I)
# 	sM  = sXtTXt + mu*sI
# 	print "inv of sM"
# 	sMinv = sparse.linalg.inv(sM)	
# 	print sMinv.shape
# 	sM2 = sMinv*sXtT
# 	print "Compute A"
# 	sA     = sX*sM2
# 	#Convert to full form
# 	A     = sA.toarray()
# 	A     = np.array(A)
# 	print 'A shape:', A.shape
	
# 	#Save A matrix into a binary NumPy file for further use
# 	np.save('A.npy',A)








# #Computes keyword of each topic using RAKE
# def update_topic_keywords():

# 	#Import data
# 	f = open('json_data.txt','r')
# 	data = json.load(f)

# 	#Import lda model
# 	ldamodel = models.LdaModel.load('/tmp/tmpldamodel')

# 	#Import document term matrix
# 	f = open('doctm.data','r')
# 	doctm = pickle.load(f)

# 	#Import topic document index list
# 	f = open('topicdocindlist.list','r')
# 	topicdocindlist = pickle.load(f)
# 	numoftopics = len(topicdocindlist)
# #
# 	doctid = np.load('doctid.npy')
# 	#Compute three keywords of each topic
# 	#Initialize rake object
# 	#each word has at least 4 characters,
# 	#each phrase at most 1 words,
# 	#each keyword appears in the text at least 10 times
# 	rake_object = rake.Rake("SmartStoplist.txt", 4, 5, 5)
# 	textcontent = ''
# 	#clusterdocinds = [0,200,110,150]
# 	topickeywords = []
# 	for topicdocinds in topicdocindlist:
# 		#print topicdocinds
# 		for i in topicdocinds:
# 			teststr      = data[i]["plainTextContent"]
# 			textcontent  = textcontent + ' ' + data[i]["plainTextContent"]
# 		topickeyword = rake_object.run(textcontent)
# 		#print topickeyword

# 		if len(topickeyword) > 0:
# 			topickeywords.append(topickeyword[0])
# 		else:
# 			topickeywords.append('test')
# 		textcontent = ''

# 	for i in range(len(topickeywords)):
# 		print topickeywords[i]
# 		#print keywords[0:2]

# 	#Show top topics
# 	#print ldamodel.top_topics(doctm, num_words=10)
