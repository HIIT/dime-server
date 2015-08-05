#!/usr/local/lib/python2.7
# -*- coding: utf-8 -*-

# For DiMe server queries
import requests
import socket
import json

#For importing and exporting lists
import pickle

#
import numpy as np

#For LDA (Latent dirichlet allocation)
import gensim
from gensim import corpora, models, similarities, interfaces

#for comparing words 
#Learn tfidf model from the document term matrix
import difflib

#
from update_dict_lda_and_Am import *

#
#import matplotlib.pyplot as plt


#####
#Some additional functions that are used in search_dime function





#Remove unwanted words
def remove_unwanted_words(testlist):
    #Load stopwordlist
    cpath = os.getcwd()
    cpathd= cpath + '/' + 'data/' + 'stopwordlist.list'
    f = open(cpathd,'r')
    stoplist = pickle.load(f)

    chgd = True
    if len(testlist) > 0:
        for iword, word in enumerate(testlist):
            while chgd:
                if not iword > len(testlist)-1:
                    if testlist[iword] in stoplist:
                        del testlist[iword]
                        chgd = True
                    else:
                        chgd = False
                else:
                    break
            chgd = True

    return testlist



################################################################


def search_dime(srvurl, username, password, query):
    #------------------------------------------------------------------------------

    #server_url = 'http://localhost:8080/api'
    server_url = str(srvurl)
    server_username = str(username)
    server_password = str(password)

    #------------------------------------------------------------------------------

    # ping server (not needed, but fun to do :-)
    r = requests.post(server_url + '/ping')

    if r.status_code != requests.codes.ok:
        print('No connection to DiMe server!')
        sys.exit(1)

    r = requests.get(server_url + '/search?query={}&limit=5'.format(query),
        	         headers={'content-type': 'application/json'},
                	 auth=(server_username, server_password),
                     timeout=10)

    #print query

    if r.status_code != requests.codes.ok:
        print('No results from DiMe database!')
        r = None
    else:
        if len(r.json()) > 0:
            r = r.json()
            print 'Search thread: number of data objects: ', len(r)
            return r



#
def search_dime_docsim(query):

    #Get current path

    cpath  = os.getcwd()
    cpathd = cpath + '/' + 'data'
    if os.path.exists(cpathd):
        os.chdir(cpathd)
    else:
        check_update()
        os.chdir(cpathd)

    #Import data
    json_data = open('json_data.txt')
    data = json.load(json_data)

    #Load index into which the query is compared
    index = similarities.docsim.Similarity.load('/tmp/similarityvec')

    #Import dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

    #
    f = open('varlist.list','r')
    varlist = pickle.load(f)
    nword = varlist[0]
    ndocuments = varlist[1]

    #
    f = open('docindlist.list','r')
    docinds = pickle.load(f)
    
    #Import document term matrix
    f = open('doctm.data','r')
    doctm = pickle.load(f)

    #
    os.chdir('../')

    #Make wordlist from the query string
    test_wordlist = query.lower().split()
    #print test_wordlist
    #Remove words belonging to stoplist
    test_wordlist = remove_unwanted_words(test_wordlist)
    #print test_wordlist

    #Convert the words into nearest dictionary word
    for nword, word in enumerate(test_wordlist):
        correctedword = difflib.get_close_matches(word, dictionary.values())
        if len(correctedword):
            test_wordlist[nword] = correctedword[0]
        else:
            test_wordlist[nword] = ' '
    print "Search thread: Closest dictionary words: ", test_wordlist

    # Convert the wordlist into bag of words (bow) representation
    test_vec = dictionary.doc2bow(test_wordlist)

    #Find the indices of most similar documents
    doclist = index[test_vec]
    print 'Search thread: docinds of DocSim: ', doclist

    #Take indices of similar documents
    docinds = []
    for i, d in enumerate(doclist):
        docinds.append(doclist[i][0])

    #
    jsons = []
    for i in range(len(docinds)):
        #print docinds[i]
        jsons.append(data[docinds[i]])
    
    # print len(jsons)   
    return jsons[0:20], docinds[0:20]


#
def search_dime_lda(query):

    # Read list of forbidden words #
    f = open('stopwordlist.list', 'r')
    stoplist = pickle.load(f)

    #Import data
    json_data = open('json_data.txt')
    data = json.load(json_data)

    #Import dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

    #Import lda model
    ldamodel = models.LdaModel.load('/tmp/tmpldamodel')

    #Import document term matrix
    f = open('doctm.data','r')
    doctm = pickle.load(f)

    #Number of documents
    ndocuments = len(doctm)
    
    #Make wordlist from the query string
    test_wordlist = query.lower().split()
    print test_wordlist
    #Remove words belonging to stoplist
    test_wordlist = remove_unwanted_words(test_wordlist, stoplist)
    print test_wordlist


    #Convert the words into nearest dictionary word
    for nword, word in enumerate(test_wordlist):
        correctedword = difflib.get_close_matches(word, dictionary.values())
        if len(correctedword):
            test_wordlist[nword] = correctedword[0]
        else:
            test_wordlist[nword] = ' '
    print "Closest dictionary words: ", test_wordlist

    # Convert the wordlist into bag of words (bow)
    test_vec = dictionary.doc2bow(test_wordlist)

    # Compute cluster (topic) probabilities
    test_lda  = ldamodel[test_vec]

    #Compute the topic index of the test document (query)
    dumtidv = []
    dumtpv  = []
    for j in range(len(test_lda)):
        dumtidv.append(test_lda[j][0])
        dumtpv.append(test_lda[j][1])
    #
    ttid = dumtidv[np.argmax(dumtpv)]

    #Show the words included in the topic
    #prkw = ldamodel.show_topic(ttid, topn=10)
    prkw = ldamodel.show_topic(ttid)

    #Print ten keywords 
    for i in range(len(prkw)):
        print prkw[i][1]
 
    #Compute topic ids for visited resources (web-pages, docs, emails, etc..)
    dtid = []
    for i in range(len(doctm)):
        dumtidv = []
        dumtpv  = []
        doc_lda = ldamodel[doctm[i]]
        for j in range(len(doc_lda)):
                dumtidv.append(doc_lda[j][0])
                dumtpv.append(doc_lda[j][1])
        dtid.append(dumtidv[np.argmax(dumtpv)])
    #
    dtid = np.array(dtid)

    # Give uri of documents that are in cluster of index ttid (in the same cluster as the test document)
    docinds = np.where(dtid == ttid)[0]

    #Return the json objects that are in the same
    #cluster
    jsons = []
    for i in range(len(docinds)):
        #print docinds[i]
        jsons.append(data[docinds[i]])
    
    print len(jsons)
    
    return jsons[0:5]

#
def search_dime_linrel_summing_previous_estimates(query):
    
    #Get current path
    cpath  = os.getcwd()
    print 'LinRel: ', cpath
    #cpathd = cpath + '/' + 'data'
    #os.chdir(cpathd)

    #Import data
    json_data = open('data/json_data.txt', 'r')
    data = json.load(json_data)    

    #Import dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

    #Open docindlist (the list of indices of suggested documents
    f = open(cpath + '/data/docindlist.list','r')
    docinds = pickle.load(f)
    #Sort from smallest to largest index value
    #docinds.sort() 
    print 'Search thread: Old docindlist: ', docinds

    #
    f = open('data/varlist.list', 'r')
    varlist = pickle.load(f)
    nwords = varlist[0]
    ndocuments = varlist[1]

    #Import tfidf model by which the relevance scores are computed 
    tfidf = models.TfidfModel.load('data/tfidfmodel.model')

    #Make wordlist from the query string
    test_wordlist = query.lower().split()
    #Remove unwanted words from query
    test_wordlist = remove_unwanted_words(test_wordlist)

    #Convert the words into nearest dictionary word
    for nword, word in enumerate(test_wordlist):
        correctedword = difflib.get_close_matches(word, dictionary.values())
        if len(correctedword):
            test_wordlist[nword] = correctedword[0]
        else:
            test_wordlist[nword] = ' '
    print "Search thread: Closest dictionary words: ", test_wordlist

    #Make bag of word vector of the input string taken from keyboard
    test_vec = dictionary.doc2bow(test_wordlist)

    #
    kws = return_and_print_estimated_keyword_indices_and_values(test_vec, docinds, dictionary, nwords)
    


    #gensim.matutils.corpus2dense(corpus, num_terms, num_docs=None, dtype=<type 'numpy.float32'>)
    #x = np.arange(0, 5, 0.1);
    #y = np.sin(x)

    #Convert to tfidf vec (list of 2-tuples, (word id, tfidf value))
    test_vec = tfidf[test_vec] 
    test_vec_full = twotuplelist2fulllist(test_vec, nwords)
    #plt.plot(range(len(test_vec_full)), test_vec_full)
    #plt.show()

    #Compute relevance scores 
    #nr, nc = Xt.shape
    nc = len(docinds)
    if nc == 0:
        jsons, docinds = search_dime_docsim(query)
        docindsunsorted = docinds
        docinds.sort()
        print 'DocSim suggested inds: ', docinds
        #docinds.sort()
        cpath = os.getcwd()
        cpath = cpath + '/' + 'data'
        os.chdir(cpath)
        update_Xt_and_docindlist(docinds)
        os.chdir('../')
        y = compute_relevance_scores(docinds, test_vec)
    else:        
        #docinds.sort()
        y = compute_relevance_scores(docinds, test_vec)

    #
    print 'Search thread: length of relevance score vec (y): ', y.shape
    #print 'Search thread: Relevance scores: ', y

    #Normalize y vector
    ysum = y.sum()
    if ysum > 0:
        y = y/ysum

    #
    sy = sparse.csc_matrix(y)

    #
    sA = update_A(docinds, y)
    sy_hat = sA*sy
    y_hat  = sy_hat.toarray()
    #print 'shape of y_hat', y_hat.shape

    cpath = os.getcwd()
    cpath = cpath + '/data'
    if os.path.isfile(cpath):
        print "Search thread: updating y_hat" 
        y_hat_prev = np.load('data/y_hat_prev.npy')
        if len(y_hat) == len(y_hat_prev):
            print 'Search thread: update y_hat (by y_hat = y_hat + y_hat_prev)'
            y_hat = y_hat + y_hat_prev
        #Normalize y_hat
        y_hat_sum = y_hat.sum()
        if y_hat_sum > 0:
            y_hat = y_hat/y_hat_sum
        #
        os.chdir(cpath)
        np.save(cpath + '/y_hat_prev.npy', y_hat)
        os.chdir('../')
    else:
        #Normalize y_hat
        y_hat_sum = y_hat.sum()
        if y_hat_sum > 0:
            y_hat = y_hat/y_hat_sum        
        print "Search thread: Saving y_hat first time"
        os.chdir(cpath)
        np.save(cpath + '/y_hat_prev.npy', y_hat)
        os.chdir('../')        
        #np.save(cpathd + '/y_hat_prev.npy', y_hat)

    #
    print 'Search thread: y_hat max:', y_hat.max(), 'y_hat argmax:', y_hat.argmax()

    #Compute upper bound on the deviation of the relevance estimate using matrix A
    sigma_hat = np.sqrt(sA.multiply(sA).sum(1)) 
    sigma_hat = np.array(sigma_hat)

    print 'Search thread: sigma_hat max:', sigma_hat.max(), ', sigma_hat argmax: ', sigma_hat.argmax()


    #Coefficient determining the importance of deviation of the relevance vector
    #in search
    c = 0.0

    #Compute doc. indices
    if sigma_hat.max() == 0:
        print "Search thread: LinRel don't suggest anything, use DocSim"
        docs, docinds = search_dime_docsim(query)
        #docinds.sort()
        #pass
    else: 
        #
        #print 'shape y_hat,', y_hat.shape, 'type: ', type(y_hat)
        #print 'shape sigma_hat,', sigma_hat.shape, 'type: ', type(sigma_hat)
        e = np.array(y_hat + (c/2)*sigma_hat)
        #print e
        #print 'e shape,', e.shape
        print 'Search thread: e max:', e.max(), 'e argmax:', e.argmax()
        #print e.shape

        docinds= np.argsort(e[:,0])
        docinds= docinds[-20:]
        docinds= docinds.tolist()
        #print docinds
    #print type(docinds)
    #print docinds
    #docinds.sort()
    #print 'Search thread: New docindlist: ', docinds


    #Get jsons
    jsons = []
    for i in range(len(docinds)):
        #print docinds[i]
        jsons.append(data[docinds[i]])

    docinds.sort()
    cpath = os.getcwd()
    os.chdir(cpath + '/data')
    update_Xt_and_docindlist(docinds)
    os.chdir('../')

    return jsons[-20:], kws


#
def search_dime_linrel_without_summing_previous_estimates(query):
    #print 'NEGLECTING HISTORY!!!'

    #Get current path
    cpath  = os.getcwd()
    print 'LinRel: ', cpath
    #cpathd = cpath + '/' + 'data'
    #os.chdir(cpathd)

    #Import data
    json_data = open('data/json_data.txt', 'r')
    data = json.load(json_data)    

    #Import dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

    #Open docindlist (the list of indices of suggested documents
    f = open(cpath + '/data/docindlist.list','r')
    docinds = pickle.load(f)
    #Sort from smallest to largest index value
    #docinds.sort() 
    print 'Search thread: Old docindlist: ', docinds

    #
    f = open('data/varlist.list', 'r')
    varlist = pickle.load(f)
    nwords = varlist[0]
    ndocuments = varlist[1]

    #Import tfidf model by which the relevance scores are computed 
    tfidf = models.TfidfModel.load('data/tfidfmodel.model')

    #Make wordlist from the query string
    test_wordlist = query.lower().split()

    #Remove unwanted words from query
    test_wordlist = remove_unwanted_words(test_wordlist)

    #Convert the words into nearest dictionary word
    for nword, word in enumerate(test_wordlist):
        correctedword = difflib.get_close_matches(word, dictionary.values())
        if len(correctedword):
            test_wordlist[nword] = correctedword[0]
        else:
            test_wordlist[nword] = ' '
    print "Search thread: Closest dictionary words: ", test_wordlist
    test_vec = dictionary.doc2bow(test_wordlist)
    #Convert to tfidf vec (list of 2-tuples, (word id, tfidf value))
    test_vec = tfidf[test_vec] 

    #Compute relevance scores 
    #nr, nc = Xt.shape
    nc = len(docinds)
    if nc == 0:
        jsons, docinds = search_dime_docsim(query)
        docindsunsorted = docinds
        docinds.sort()
        print 'DocSim suggested inds: ', docinds
        #docinds.sort()
        cpath = os.getcwd()
        cpath = cpath + '/' + 'data'
        os.chdir(cpath)
        update_Xt_and_docindlist(docinds)
        os.chdir('../')
        y = compute_relevance_scores(docinds, test_vec)
    else:        
        #docinds.sort()
        y = compute_relevance_scores(docinds, test_vec)

    #
    print 'Search thread: length of relevance score vec (y): ', y.shape
    print 'Search thread: Relevance scores: ', y

    #Normalize y vector
    ysum = y.sum()
    if ysum > 0:
        y = y/ysum

    #
    sy = sparse.csc_matrix(y)

    #
    sA = update_A(docinds, y)
    sy_hat = sA*sy
    y_hat  = sy_hat.toarray()
    #print 'shape of y_hat', y_hat.shape

    cpath = os.getcwd()
    cpath = cpath + '/data'
    if os.path.isfile(cpath):
        print "Search thread: updating y_hat" 
        y_hat_prev = np.load('data/y_hat_prev.npy')
        if len(y_hat) == len(y_hat_prev):
            print 'Search thread: update y_hat (by y_hat = y_hat + y_hat_prev)'
            y_hat = y_hat + y_hat_prev
        #Normalize y_hat
        y_hat_sum = y_hat.sum()
        if y_hat_sum > 0:
            y_hat = y_hat/y_hat_sum
        #
        os.chdir(cpath)
        np.save(cpath + '/y_hat_prev.npy', y_hat)
        os.chdir('../')
    else:
        #Normalize y_hat
        y_hat_sum = y_hat.sum()
        if y_hat_sum > 0:
            y_hat = y_hat/y_hat_sum        
        print "Search thread: Saving y_hat first time"
        os.chdir(cpath)
        np.save(cpath + '/y_hat_prev.npy', y_hat)
        os.chdir('../')        
        #np.save(cpathd + '/y_hat_prev.npy', y_hat)

    #
    print 'Search thread: y_hat max:', y_hat.max(), 'y_hat argmax:', y_hat.argmax()

    #Compute upper bound on the deviation of the relevance estimate using matrix A
    sigma_hat = np.sqrt(sA.multiply(sA).sum(1)) 
    sigma_hat = np.array(sigma_hat)

    print 'Search thread: sigma_hat max:', sigma_hat.max(), ', sigma_hat argmax: ', sigma_hat.argmax()


    #Coefficient determining the importance of deviation of the relevance vector
    #in search
    c = 0.0

    #Compute doc. indices
    if sigma_hat.max() == 0:
        print "Search thread: LinRel don't suggest anything, use DocSim"
        docs, docinds = search_dime_docsim(query)
        #docinds.sort()
        #pass
    else: 
        #
        #print 'shape y_hat,', y_hat.shape, 'type: ', type(y_hat)
        #print 'shape sigma_hat,', sigma_hat.shape, 'type: ', type(sigma_hat)
        e = np.array(y_hat + (c/2)*sigma_hat)
        #print e
        #print 'e shape,', e.shape
        print 'Search thread: e max:', e.max(), 'e argmax:', e.argmax()
        #print e.shape

        docinds= np.argsort(e[:,0])
        docinds= docinds[-20:]
        docinds= docinds.tolist()
        #print docinds
    #print type(docinds)
    #print docinds
    #docinds.sort()
    #print 'Search thread: New docindlist: ', docinds


    #Get jsons
    jsons = []
    for i in range(len(docinds)):
        #print docinds[i]
        jsons.append(data[docinds[i]])

    docinds.sort()
    cpath = os.getcwd()
    os.chdir(cpath + '/data')
    update_Xt_and_docindlist(docinds)
    os.chdir('../')

    return jsons[-20:]



#Computes cosine similarity between input vec. (test_vec) and previously
#suggested documents and returns vector of these similarities
def compute_relevance_scores(docinds, test_vec):
    #suggested_docs in the form of full document term matrix 

    sX = load_sparse_csc('data/sX.sparsemat.npz')    

    print "Search thread: Updating A"
    #F
    #X  = np.load('X.npy')
    #Xt = np.load('Xt.npy')
    #Compute estimation of weight vector 
    print 'Search thread: Create Xt '
    print 'Search thread: X shape, ', sX.shape
    sXcsr = sX.tocsr()
    sXtcsr= sXcsr[docinds,:]
    sXtcsc= sXtcsr.tocsc()
    Xt    = sXtcsc.toarray()
    print 'Search thread: Xt shape, ', Xt.shape

    #Convert Xt to corpus form
    nr, nc = Xt.shape
    Xtlist = []
    for i in range(nr):
        Xtlist.append( gensim.matutils.full2sparse(Xt[i][:]) )
        #print len(Xtlist[i])
    #print 'Xt len:', len(Xtlist)

    #Compute relevance scores
    nr = len(Xtlist)
    y = []
    for i in range(nr):
        y.append(gensim.matutils.cossim(test_vec,Xtlist[i]))
        #print y[i]
    y = np.asarray([y])
    y = y.transpose()
    nr, nc = y.shape

    return y

def twotuplelist2fulllist(tuplelist, nfeatures):
    if len(tuplelist) == 0:
        vec = [0]*nfeatures
        #pass
    else:
        #
        vec = [0]*nfeatures
        nel = len(tuplelist[0])
        #print 'Num. of el.:', nel
        for i in range(len(tuplelist)):
            vec[tuplelist[i][0]] = tuplelist[i][1]

    vec = np.array(vec)
    print 'Length of wordlist: ', len(vec)
    return vec


def return_and_print_estimated_keyword_indices_and_values(test_vec, docinds, dictionary, nwords):
    #Make relevance vector 'r' of keywords (i.e. vector of zeros and ones , i.e. vector answering question, 
    #whether keyboard input contain keywords or not)
    test_vec_full = twotuplelist2fulllist(test_vec, nwords)
    inds          = np.where(test_vec_full)
    r             = np.zeros(test_vec_full.shape)
    r[inds]       = 1.0
    print 'Number of keywords in keyboard input: ', np.where(r>0)
    #
    r_hat = return_keyword_relevance_estimates(docinds, r)
    kwinds= np.argsort(r_hat[:,0])
    #kwinds= np.argsort(r_hat)
    print 'Estimated Keyword weights: ', r_hat
    kwinds= kwinds[-20:]
    #Make reverse list object
    kwindsrev = reversed(kwinds)
    #Reverse
    kwindsd = []
    for i in kwindsrev:
        kwindsd.append(i)
    #
    kwinds = kwindsd
    #Initialize list of keywords
    kws = []
    #print 'Indices of estimated keywords: ', kwinds
    #kwinds= docinds.tolist()
    for i in range(len(kwinds)):
        print 'Suggested keywords: ', dictionary.get(kwinds[i]) 
        kws.append(dictionary.get(kwinds[i]))

    return kws



#Updates LinRel matrix, denoted by A 
def return_keyword_relevance_estimates(docinds, y):

    #Load sparse tfidf matrix
    #sX = np.load('sX.npy')
    sX = load_sparse_csc('data/sX.sparsemat.npz')

    print "Search thread: update_keyword_matrix: Updating A"

    #Compute estimation of weight vector (i.e. user model)
    print 'Search thread: Create Xt '
    sXcsr = sX.tocsr()
    print 'Search thread: Type of sXcsr: ', type(sXcsr)
    sXtcsr= sXcsr[docinds,:]
    Xt    = sXtcsr.toarray()
    #TRANSPOSE!!
    Xt    = Xt.transpose()

    print 'Search thread: update_keyword_matrix: Xt shape: ', Xt.shape, ' type: ', type(Xt)
    print 'Search thread: update_keyword_matrix: min val Xt: ', Xt.min()

    print 'Search thread: update_keyword_matrix: y shape: ', y.shape
    #
    w_hat = estimate_w(Xt,y)
    w_hat = np.array([w_hat])
    w_hat = w_hat.transpose()

    print 'Search thread: update_keyword_matrix: w shape: ', w_hat.shape, ' type: ', type(w_hat)
    r_hat = np.dot(Xt,w_hat)
    print 'Search thread: update_keyword_matrix: r_hat shape: ', r_hat.shape, ' type: ', type(r_hat)
    print 'Search thread: update_keyword_matrix: max val r_hat: ', r_hat.max()
    return r_hat

#Compute Tikhonov regularized solution for y=Xt*w (using scipy function lsqr)
#I.e. compute estimation of user model
def estimate_w(Xt,y):
    #
    #mu = 1.5
    mu = 0.0
    w = scipy.sparse.linalg.lsqr(Xt,y, damp=mu)[0]
    return w