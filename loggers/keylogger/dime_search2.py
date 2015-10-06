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
from update_files import *

#
import math

#
from math_utils import *

#
import scipy.cluster
#
#import matplotlib.pyplot as plt


#####
#Some additional functions that are used in search_dime function
#
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
    #print 'Length of wordlist: ', len(vec)
    return vec

#Remove unwanted words
def remove_unwanted_words(testlist):
    #Load stopwordlist
    cpath = os.getcwd()
    cpathd= cpath + '/' + 'data/' + 'stopwordlist.list'
    #f = open(cpathd,'r')
    #stoplist = pickle.load(f)
    stoplist = pickle.load(open(cpathd,'rb'))

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
#Search functions 
################################################################

#Search using DiMe-server's own search function
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

    #try:
    #    query_str = query.encode('utf-8')
    #except UnicodeEncodeError:
    #    print("<UnicodeEncodeError>")
    #    return []

    #print("DiMe query string:", query)
    #
    r = requests.get(server_url + '/search?query={}&limit=5'.format(query),
                     headers={'content-type': 'application/json'},
                     auth=(server_username, server_password),
                     timeout=100)
    # r = requests.get(server_url + '/search?query={}&limit=60'.format(query),
    #                  headers={'content-type': 'application/json'},
    #                  auth=(server_username, server_password),
    #                  timeout=10)

    #print(r.json())

    if r.status_code != requests.codes.ok:
        print('No results from DiMe database!')
        return []
    elif len(r.json()) > 0:
            r = r.json()
            print('Search thread: number of data objects: ', len(r))
            return r
    else: 
        print('Search thread: number of data objects: 0')
        return []


#Search using gensim's cossim-function (cosine similarity)
def search_dime_docsim(query, data, index, dictionary):
    #
    #f = open('data/varlist.list','r')
    #varlist = pickle.load(f)
    varlist = pickle.load(open('data/varlist.list','rb'))
    nword = varlist[0]
    ndocuments = varlist[1]
    
    #Make wordlist from the query string
    test_wordlist = query.lower().split()

    #Remove words belonging to stoplist
    test_wordlist = remove_unwanted_words(test_wordlist)

    #Map the input words into nearest dictionary words
    for nword, word in enumerate(test_wordlist):
        correctedword = difflib.get_close_matches(word, list(dictionary.values()))
        if len(correctedword):
            test_wordlist[nword] = correctedword[0]
        else:
            test_wordlist[nword] = ' '
    #print "Search thread: Closest dictionary words: ", test_wordlist

    # Convert the wordlist into bag of words (bow) representation
    test_vec = dictionary.doc2bow(test_wordlist)

    #Find the indices of the most similar documents
    doclist = index[test_vec]

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


#Function that computes keywords using LinRel and makes search using
#'search_dime_docsim'
def search_dime_linrel_keyword_search(query, X, data, index, tfidf, dictionary, c):

    #Inputs:
    #query = string from keyboard
    #X     = document term matrix as tfidf form
    #tfidf = tfidf -model by which the query is transformed into a tfidf vector
    #dictionary = list of words and their indices ['word    ']
    #c     = Exploitation/Exploration coefficient
    #
    #Outputs:
    #jsons = links to resources
    #kws   = keywords computed by LinRel

    #
    ndocuments = X.shape[0]
    nwords     = len(dictionary)

    #Convert query into bag of words representation urheilu yle 
    test_vec      = query2bow(query, dictionary)

    #
    winds, kws = return_and_print_estimated_keyword_indices_and_values(test_vec, dictionary, c)
    kws_vec    = dictionary.doc2bow(kws)

    #make string of keywords 
    kwsstr = ''
    for i in range(len(kws)):
        kwsstr = kwsstr + ' ' + kws[i]
    #print 'Keyword query string: ', kwsstr
    
    #Make
    if len(kws) > 0:
        #jsons, docinds = search_dime_docsim(kwsstr)
        jsons, docinds = search_dime_docsim(query, data, index, dictionary)
    else:
        #print 'QUERY: ', query
        jsons, docinds = search_dime_docsim(query, data, index, dictionary)
        kws = []

    docinds.sort()
    cpath = os.getcwd()
    update_Xt_and_docindlist(docinds)

    return jsons, kws


#Function that computes keywords using LinRel and makes search using
#DiMe-server's own search function, 'search_dime'
def search_dime_linrel_keyword_search_dime_search(query, X, tfidf, dictionary, c, srvurl, username, password):

    #Inputs:
    #query = string from keyboard
    #X     = document term matrix as tfidf form
    #tfidf = tfidf -model by which the query is transformed into a tfidf vector
    #dictionary = list of words and their indices ['word    ']
    #c     = Exploitation/Exploration coefficient

    #Outputs:
    #jsons = list jsons corresponding each resource 
    #kws   = keywords computed by LinRel

    #
    ndocuments = X.shape[0]
    nwords     = len(dictionary)

    #Convert query into bag of words representation urheilu yle 
    test_vec      = query2bow(query, dictionary)

    #Get keywords related to input query string 
    winds, kws = return_and_print_estimated_keyword_indices_and_values(test_vec, X, dictionary, c)

    #make string of keywords 
    query = '%s' % query

    #Search resources from DiMe using Dime-servers own search function
    jsons = search_dime(srvurl, username, password, query)

    return jsons, kws, winds

#
def query2bow(query,dictionary):

    #inputs:
    #query      = string input
    #dictionary = gensim dictionary containing words taken from dime data

    #Output:
    #test_vec   = bag of word representation of query string


    #Make list of words from the query string
    test_wordlist = query.lower().split()
    #Remove unwanted words from query
    test_wordlist = remove_unwanted_words(test_wordlist)

    #Convert the words into nearest dictionary word
    for nword, word in enumerate(test_wordlist):
        correctedword = difflib.get_close_matches(word, list(dictionary.values()))
        if len(correctedword):
            test_wordlist[nword] = correctedword[0]
        else:
            test_wordlist[nword] = ' '
    print(("Search thread: Closest dictionary words: ", test_wordlist))
    #f = open('data/test_wordlist.list','w')
    #pickle.dump(test_wordlist,f)
    pickle.dump(test_wordlist, open('data/test_wordlist.list','wb'))

    #Make bag of word vector of the input string taken from keyboard
    test_vec = dictionary.doc2bow(test_wordlist)

    return test_vec

#
def return_and_print_estimated_keyword_indices_and_values(test_vec, X, dictionary, c):

    #Inputs:
    #test_vec   = bag of word representation of the input query string (taken from keyboard)
    #X          = tfidf matrix of resources
    #dictionary = gensim dictionary containing words taken from dime data
    #c          = Exploitation/Exploration coefficient

    #Output:
    #vsinds     = list of indices of keywords
    #kws        = list of keywords

    #Number of words in dictionary
    nwords = len(dictionary)

    #Full vector representation of test_vec (i.e. containing all word indices)
    test_vec_full = twotuplelist2fulllist(test_vec, nwords)

    #Take indices of words occurring in the input
    winds         = np.where(test_vec_full)
    winds         = winds[0]

    #Form observed relevance vector from test_vec_full
    #If old observed relevance vector exists, add it to new relevance vector
    if os.path.isfile('data/r_old.npy'):

        #Load 
        r             = np.zeros([test_vec_full.shape[0],1])
        r_old         = np.load('data/r_old.npy')
        oldwinds      = np.where(r_old)
        r[oldwinds]   = 1.0
        #Add old observed relevance vector into new one
        r             = r + r_old
        r[winds]      = 1.0
        np.save('data/r_old.npy',r)

        #Take inverse of all non-zeros of elements of r = r + r_old
        thresval = 0.1
        for i in range(len(r)):
            if float(r[i]) > 0.0:
                #
                r[i] = 1.0/float(r[i])
                #If value is less than thresval, put to zero
                if float(r[i]) < thresval:
                    #print("PUTTING TO ZERO!!!!!!")
                    r[i] = 0.0
    else:
        r             = np.zeros([test_vec_full.shape[0],1])
        r[winds]      = 1.0
        np.save('data/r_old.npy',r)

    #Regularization paramter
    mu = 1.0

    #Compute relevance estimate vector r_hat, and sigma_hat (= upper bound vector of st.dev vector of r_hat)
    #r_hat, sigma_hat = return_keyword_relevance_and_variance_estimates_woodbury(r, X, mu)
    #r_hat, sigma_hat = return_keyword_relevance_and_variance_estimates_woodbury_csc(r, X, mu)
    r_hat, sigma_hat, w_hat = return_keyword_relevance_and_variance_estimates_woodbury_csc_clear(r, X, mu)
    #print("w_hat!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:", w_hat)


    #Compute to norm of sigma_hat
    norm_sigma_hat = np.linalg.norm(sigma_hat)
    if os.path.isfile("data/norm_sigma_hat.npy"):
        norm_sigma_hat_vec = np.load("data/norm_sigma_hat.npy")
        norm_sigma_hat_vec = np.append(norm_sigma_hat_vec, norm_sigma_hat)
        np.save('data/norm_sigma_hat.npy', norm_sigma_hat_vec)
    else:
        norm_sigma_hat_vec = np.array([norm_sigma_hat])
        np.save('data/norm_sigma_hat.npy', norm_sigma_hat_vec)



    #Normalize relevance estimate vector
    if r_hat.sum() > 0.0:
        r_hat     = r_hat/r_hat.sum()
    #Normalize sigma_hat (upper bound std.dev of relevance estimates)
    if sigma_hat.sum() > 0.0:
        sigma_hat = sigma_hat/sigma_hat.sum()
    #Make unit vector from w_hat (user model)
    norm_w_hat = np.linalg.norm(w_hat)
    if norm_w_hat > 0.0:
        w_hat = w_hat/norm_w_hat
        norm_w_hat = np.linalg.norm(w_hat)
        #print("Norm of current w_hat: ", np.linalg.norm(w_hat))
        #w_hat = w_hat/w_hat.sum()

    #Add r_hat and sigma_hat, where c = Exploitation/Exploration coeff.
    vsum = r_hat + c*sigma_hat
    #Normalize vsum
    if vsum.max() > 0.0:
        vsum = vsum/vsum.sum()

    #Compute sparsities of vectors
    r_hat_spar     = vec_sparsity(r_hat)
    #Store sparsity values of r_hat vector
    if os.path.isfile("data/r_hat_spar_hist_vec.npy"):
        r_hat_spar_hist_vec = np.load('data/r_hat_spar_hist_vec.npy')
        r_hat_spar_hist_vec = np.append(r_hat_spar_hist_vec, r_hat_spar)
        np.save('data/r_hat_spar_hist_vec.npy', r_hat_spar_hist_vec)
    else:
        r_hat_spar_hist_vec = np.array([r_hat_spar])
        np.save('data/r_hat_spar_hist_vec.npy', r_hat_spar_hist_vec)

    sigma_hat_spar = vec_sparsity(sigma_hat)
    #Store sparsity values of sigma_hat vector
    if os.path.isfile("data/sigma_hat_spar_hist_vec.npy"):
        sigma_hat_spar_hist_vec = np.load('data/sigma_hat_spar_hist_vec.npy')
        sigma_hat_spar_hist_vec = np.append(sigma_hat_spar_hist_vec, sigma_hat_spar)
        np.save('data/sigma_hat_spar_hist_vec.npy', sigma_hat_spar_hist_vec)
    else:
        sigma_hat_spar_hist_vec = np.array([sigma_hat_spar])
        np.save('data/sigma_hat_spar_hist_vec.npy', sigma_hat_spar_hist_vec)

    #
    vsum_spar      = vec_sparsity(vsum)

    #Load previous vsum -vector, and compute cosine similarity between current vsum and previous vsum vectors
    cossim = 0.0
    eps    = 1e-15
    if os.path.isfile('data/vsum.npy'):
        #print "dime_search: Load vsum_old!!"
        vsum_old = np.load('data/vsum.npy')
        #Compute cosine similarity between previous and current vsum -vectors
        cossim = vsum_old.T.dot(vsum)[0.0]
        n1 = np.linalg.norm(vsum)
        n2 = np.linalg.norm(vsum_old)   
        cossim = cossim/(max(n1*n2,eps))
    #Store cosine similarity between vsum vectors into a vector and file    
    if os.path.isfile("data/cossim_vsum_vec.npy"):
        cossim_vsum_vec = np.load('data/cossim_vsum_vec.npy')
        cossim_vsum_vec = np.append(cossim_vsum_vec, cossim)
        np.save('data/cossim_vsum_vec.npy', cossim_vsum_vec)
    else:
        cossim_vsum_vec = np.array([cossim])
        np.save('data/cossim_vsum_vec.npy', cossim_vsum_vec)        

    #Load previous w_hat -vector, and compute cosine similarity between current w_hat and previous w_hat vectors
    cossim_w_hat = 0.0
    eucl_dist_w_hat = 0.0
    eps    = 1e-15
    if os.path.isfile('data/w_hat.npy'):
        #
        w_hat_old = np.load('data/w_hat.npy')
        norm_w_hat_old = np.linalg.norm(w_hat_old)
        #print("Norm of old w_hat: ", norm_w_hat_old)
        sum_norms = norm_w_hat + norm_w_hat_old
        #print("sum of norms!!!!!!!!!!: ", sum_norms)
        #
        diff_w_hat = w_hat_old-w_hat
        eucl_dist_w_hat  = np.linalg.norm(diff_w_hat)
        eucl_dist_w_hat  = eucl_dist_w_hat/sum_norms
        print("Euclidean distance in unit sphere!: ", eucl_dist_w_hat)

    #Compute and store eucl distance between current and previous w_hat
    if os.path.isfile("data/eucl_dist_w_hat_vec.npy"):
        eucl_dist_w_hat_vec = np.load('data/eucl_dist_w_hat_vec.npy')
        eucl_dist_w_hat_vec = np.append(eucl_dist_w_hat_vec, eucl_dist_w_hat)
        np.save('data/eucl_dist_w_hat_vec.npy', eucl_dist_w_hat_vec)
    else:
        eucl_dist_w_hat_vec = np.array([eucl_dist_w_hat])
        np.save('data/eucl_dist_w_hat_vec.npy', eucl_dist_w_hat_vec)    

    #Compute and store cosine similarity between current and previous user model
    # if os.path.isfile("data/cossim_w_hat_vec.npy"):
    #     cossim_w_hat_vec = np.load('data/cossim_w_hat_vec.npy')
    #     cossim_w_hat_vec = np.append(cossim_w_hat_vec, cossim_w_hat)
    #     np.save('data/cossim_w_hat_vec.npy', cossim_w_hat_vec)
    # else:
    #     cossim_w_hat_vec = np.array([cossim_w_hat])
    #     np.save('data/cossim_w_hat_vec.npy', cossim_w_hat_vec)    

    #Save current r_hat and sigma_hat, and w_hat
    np.save('data/r_hat.npy',r_hat)
    np.save('data/sigma_hat.npy',sigma_hat)
    #Store current vsum-vector to vsum.npy
    np.save('data/vsum.npy', vsum)        
    #Store current w_hat
    np.save('data/w_hat.npy',w_hat)

    #Take take indices of elements of 'vsum' according to ascending order
    vsinds = np.argsort(vsum[:,0])
    #Take last 20 indices from vsinds
    vsinds = vsinds[-20:]
    #Make reversed list of vsinds
    vsindsrev = reversed(vsinds)
    #Reverse
    vsinds = []
    for i in vsindsrev:
        vsinds.append(i)

    #Take take indices of elements of 'r_hat' according to ascending order
    kwinds = np.argsort(r_hat[:,0])
    #Take last 20 indices from vsinds
    kwinds = kwinds[-20:]
    #Make reverse list object
    kwindsrev = reversed(kwinds)
    #Reverse
    kwindsd = []
    for i in kwindsrev:
        kwindsd.append(i)
    #
    kwinds = kwindsd

    #
    if r_hat.max() > 0.0:
        #Initialize list of keywords
        kws = []
        #
        for i in range(len(vsinds)):
            #print 'Suggested keywords by vsinds: ', dictionary.get(vsinds[i]), type(dictionary.get(vsinds[i])), vsum[vsinds[i]]
            kws.append(dictionary.get(vsinds[i]))
        #
        return vsinds, kws
    else:
        return [], []


def return_keyword_relevance_and_variance_estimates_woodbury(y, sX, mu):

    #Inputs
    #y = observed relevance vector
    #sX= tfidf matrix in scipy sparse matrix format
    #mu= regularization parameter

    #Output
    #y_hatapp     = estimation of relevance vector 
    #sigma_hatapp = estimation of sigma vector (i.e. the upperbound value vector of st.dev of r_hat)


    #Load document term matrix 
    #sX = load_sparse_csc('data/sX.sparsemat.npz')
    #Make transpose of document term matrix 
    sX = sX.T
    sX = sX.tocsr()

    #Take indices of non-zeros of y-vector
    inds = np.where(y)[0]
    #print 'inds: ', inds

    #Form new y that has only non-zeros of the original y
    if len(inds) > 1:
        y    = y[inds]
    else:
        if len(inds) == 0:
            y    = np.zeros([1,1])
            inds = np.array([[0]])
        else:
            y    = np.zeros([len(inds),1])
            #inds = np.array([[0]])

    #Take rows from sX corresponding the indices of observed words from (keyboard) input
    sXt   = sX[inds,:]
    sXtT  = sXt.transpose()

    #Make identity matrices needed in further steps
    speye  = sparse.identity(sXtT.shape[0])
    speye2 = sparse.identity(sXtT.shape[1])

    #Compute XX^T
    sXtsXtT = sXt.dot(sXtT)
    #Compute A matrix 
    sdumA = (1/mu)*sXtsXtT + speye2

    #
    if sdumA.shape[0] == 1 and sdumA.shape[1] == 1:
        if sdumA[0,0] > 0.0:
            sdumAinv = sparse.csr_matrix([[1.0/sdumA[0,0]]])
        else:
            sdumAinv = sparse.csr_matrix([[1.0]])
    else:
        #Compute inverse of sdumA
        sdumAinv = sparse.linalg.inv(sdumA)
        sdumAinv.tocsr()

    #print sdumAinv.shape
    muI      = (1/mu)*speye
    sdumAinv2= speye2 - (1/mu)*sdumAinv.dot(sXtsXtT)
    sAtilde  = (1/mu)*sXtT.dot(sdumAinv2)
    sA       = sX.dot(sAtilde)

    #
    sy = sparse.csr_matrix(y)
    sy_hatapp= sA.dot(sy)
    y_hatapp= sy_hatapp.toarray()

    #
    sigma_hatapp= np.sqrt(sA.multiply(sA).sum(1)) 
    #Convert to numpy array
    sigma_hatapp= np.array(sigma_hatapp)

    return y_hatapp, sigma_hatapp    




def return_keyword_relevance_and_variance_estimates_woodbury_csc(y, sX, mu):

    #Inputs
    #y = observed relevance vector
    #sX= tfidf matrix in scipy sparse matrix format
    #mu= regularization parameter

    #Output
    #y_hatapp     = estimation of relevance vector 
    #sigma_hatapp = estimation of sigma vector (i.e. the upperbound value vector of st.dev of r_hat)


    #Load document term matrix 
    #sX = load_sparse_csc('data/sX.sparsemat.npz')
    #Make transpose of document term matrix 
    sX = sX.T
    sX = sX.tocsc()

    #Take indices of non-zeros of y-vector
    inds = np.where(y)[0]
    #print 'inds: ', inds

    #Form new y that has only non-zeros of the original y
    if len(inds) > 1:
        y    = y[inds]
    else:
        if len(inds) == 0:
            y    = np.zeros([1,1])
            inds = np.array([[0]])
        else:
            y    = np.zeros([len(inds),1])
            #inds = np.array([[0]])

    #Take rows from sX corresponding the indices of observed words from (keyboard) input
    sXt   = sX[inds,:]
    sXtT  = sXt.transpose()

    #Make identity matrices needed in further steps
    speye  = sparse.identity(sXtT.shape[0])
    speye2 = sparse.identity(sXtT.shape[1])

    #Compute XX^T
    sXtsXtT = sXt.dot(sXtT)
    #Compute A matrix 
    sdumA = (1/mu)*sXtsXtT + speye2

    #
    if sdumA.shape[0] == 1 and sdumA.shape[1] == 1:
        if sdumA[0,0] > 0.0:
            sdumAinv = sparse.csc_matrix([[1.0/sdumA[0,0]]])
        else:
            sdumAinv = sparse.csc_matrix([[1.0]])
    else:
        #Compute inverse of sdumA
        sdumAinv = sparse.linalg.inv(sdumA)
        sdumAinv.tocsc()

    #print sdumAinv.shape
    muI      = (1/mu)*speye
    sdumAinv2= speye2 - (1/mu)*sdumAinv.dot(sXtsXtT)
    sAtilde  = (1/mu)*sXtT.dot(sdumAinv2)
    sA       = sX.dot(sAtilde)

    #
    sy = sparse.csc_matrix(y)
    sy_hatapp= sA.dot(sy)
    y_hatapp= sy_hatapp.toarray()

    #
    sigma_hatapp= np.sqrt(sA.multiply(sA).sum(1)) 
    #Convert to numpy array
    sigma_hatapp= np.array(sigma_hatapp)

    return y_hatapp, sigma_hatapp    





def return_keyword_relevance_and_variance_estimates_woodbury_csc_clear(y, sX, mu):

    #Inputs
    #y = observed relevance vector
    #sX= tfidf matrix in scipy sparse matrix format
    #mu= regularization parameter

    #Output
    #y_hatapp     = estimation of relevance vector 
    #sigma_hatapp = estimation of sigma vector (i.e. the upperbound value vector of st.dev of r_hat)


    #Load document term matrix 
    #sX = load_sparse_csc('data/sX.sparsemat.npz')
    #Make transpose of document term matrix 
    sX = sX.T
    sX = sX.tocsc()

    #Take indices of non-zeros of y-vector
    inds = np.where(y)[0]
    #print 'inds: ', inds

    #Form new y that has only non-zeros of the original y
    if len(inds) > 1:
        y    = y[inds]
    else:
        if len(inds) == 0:
            y    = np.zeros([1,1])
            inds = np.array([[0]])
        else:
            y    = np.zeros([len(inds),1])
            #inds = np.array([[0]])

    #
    sy = sparse.csc_matrix(y)

    #Take rows from sX corresponding the indices of observed words from (keyboard) input
    sXt   = sX[inds,:]
    sXtT  = sXt.transpose()

    #Make identity matrices needed in further steps
    speye2 = sparse.identity(sXtT.shape[1])

    #Compute XX^T
    sXtsXtT = sXt.dot(sXtT)
    #Compute A matrix 
    sdumA = mu*speye2 + sXtsXtT 
    #Compute inverse of sdumA
    if sdumA.shape[0] == 1 and sdumA.shape[1] == 1:
        if sdumA[0,0] > 0.0:
            sdumAinv = sparse.csc_matrix([[1.0/sdumA[0,0]]])
        else:
            sdumAinv = sparse.csc_matrix([[1.0]])
    else:
        #Compute inverse of sdumA
        sdumAinv = sparse.linalg.inv(sdumA)
        sdumAinv.tocsc()

    #print sdumAinv.shape
    sdumAinv2= speye2 - sdumAinv.dot(sXtsXtT)
    sAtilde  = (1/mu)*sXtT.dot(sdumAinv2)
    sA       = sX.dot(sAtilde)

    #Compute estimation of user intent model, w_hat
    sw_hat = sAtilde.dot(sy)
    w_hat  = sw_hat.toarray()

    #Compute estimation of y based on user model
    sy_hat = sA.dot(sy)
    y_hat  = sy_hat.toarray()

    #
    sigma_hat = np.sqrt(sA.multiply(sA).sum(1)) 
    #Convert to numpy array
    sigma_hat = np.array(sigma_hat)

    return y_hat, sigma_hat, w_hat






#
def recompute_keywords(c):
    #print 'c', c
    #Import dictionary
    dictionary = corpora.Dictionary.load('data/tmpdict.dict')

    #
    r_hat     = np.load('data/r_hat.npy')
    sigma_hat = np.load('data/sigma_hat.npy')

    #Normalize
    if r_hat.max() > 0.0:
        r_hat     = r_hat/r_hat.max()
    if sigma_hat.max() > 0.0:
        sigma_hat = sigma_hat/sigma_hat.max()

    #print 'Search thread: value of c is:', c
    vsum     = r_hat + c*sigma_hat
    #print vsum.shape
    #r_hat = return_keyword_relevance_estimates(docinds, r)
    vsinds= np.argsort(vsum[:,0])
    kwinds= np.argsort(r_hat[:,0])

    if r_hat.max() > 0.0:
        kwinds = kwinds[-20:]
        vsinds = vsinds[-20:]
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
            #print 'Suggested keywords: ', dictionary.get(kwinds[i]), type(dictionary.get(kwinds[i]))
            kws.append(dictionary.get(kwinds[i]))


        #Make reverse list object
        vsindsrev = reversed(vsinds)
        #Reverse
        vsinds = []
        for i in vsindsrev:
            vsinds.append(i)
        kws = []
        for i in range(len(vsinds)):
            #print 'Suggested keywords by vsinds: ', dictionary.get(vsinds[i]), type(dictionary.get(vsinds[i]))
            kws.append(dictionary.get(vsinds[i]))
            #kws.append(dictionary.get(kwinds[i]))
    return kws















































































# def return_keyword_relevance_and_variance_estimates_evd(y, mu):

#     #Load document term matrix 
#     sX = load_sparse_csc('data/sX.sparsemat.npz')
#     #Make transpose of document term matrix 
#     sX = sX.transpose()
#     sX = sX.tocsr()


#     #Take non-zeros from y
#     inds = np.where(y)[0]
#     print 'inds: ', inds
#     if len(inds) > 1:
#         y    = y[inds]
#         #y    = 1/y
#         #print inds, y    
#     else:
#         if len(inds) == 0:
#             y    = np.zeros([1,1])
#             inds = np.array([[0]])
#         else:
#             y    = np.zeros([len(inds),1])
#             #inds = np.array([[0]])

#     #Compute estimation of weight vector (i.e. user model)
#     print 'Search thread: update_keyword_matrix: Create Xt '
#     print 'len inds', len(inds)
#     sXt   = sX[inds,:]
#     sXtT  = sXt.transpose()
#     speye = sparse.identity(sXtT.shape[0])

#     print 'Compute A'
#     print sXtT.shape, sXt.shape, speye.shape
#     sdumA = sXtT*sXt + mu*speye
#     print sdumA.shape

#     #Dvec = vector of eigenvalues, Q = array of corresponding eigenvectors
#     n=math.floor(0.99*sdumA.shape[0])
#     m=int(sdumA.shape[0]-n)
#     print 'm ', m
#     Dvec, Q = sparse.linalg.eigsh(sdumA,k=m)
#     Dvec    = Dvec.real
#     Dvecinv = 1.0/Dvec
#     D       = np.diag(Dvec)
#     D       = sparse.csr_matrix(D)
#     Dinv    = np.diag(Dvecinv)
#     Dinv    = sparse.csr_matrix(Dinv)

#     Q  = Q.real
#     Q  = sparse.csr_matrix(Q)
#     QT = Q.transpose()    

#     #sortedeigvalinds = Dvec.argsort()
#     #print sortedeigvalinds
#     print type(Q)
#     print type(D)

#     print 'sdumAinvapp1'
#     sdumAinvapp = Q*Dinv
#     print 'sdumAinvapp2'
#     sdumAinvapp = sdumAinvapp*QT

#     #sAtilde   = sdumAinv*sXT
#     print 'sdumAinvapp3'
#     sAtilde     = sdumAinvapp*sXtT
#     print sAtilde.shape


#     #sA      = sX*sAtilde
#     print 'sAapp2'
#     sA = sX.dot(sAtilde)

#     print 'sy'
#     sy = sparse.csr_matrix(y)

#     #
#     print sy.shape
#     print sA.shape
#     #sy_hat   = sA.dot(sy)
#     sy_hatapp= sA.dot(sy)
#     sw_hat2 = sAtilde*sy
#     w_hat2  = sw_hat2.toarray()
    
#     #plt.plot(range(len(w_hat)),w_hat/w_hat.max(),'r')
#     #plt.plot(range(len(w_hat2)),w_hat2/w_hat2.max(),'b')
#     #plt.show()

#     print 'shape sy_hat: ', sy_hatapp.shape

#     sigma_hatapp= np.sqrt(sA.multiply(sA).sum(1)) 
#     sigma_hatapp= np.array(sigma_hatapp)

#     #y_hat   = sy_hat.toarray()
#     y_hatapp= sy_hatapp.toarray()

#     print 'Search thread: update_keyword_matrix: r_hat shape: ', y_hatapp.shape, ' type: ', type(y_hatapp)
#     print 'Search thread: update_keyword_matrix: argmax r_hat: ', y_hatapp.argmax()
#     print 'Search thread: update_keyword_matrix: argmax sigma_hat: ', sigma_hatapp.argmax()

#     return y_hatapp, sigma_hatapp

# #
# def return_keyword_relevance_and_variance_estimates_auer(y, mu):

#     #Parameters
#     minLambda = 0.5

#     #Load document term matrix 
#     sX = load_sparse_csc('data/sX.sparsemat.npz')
#     #Make transpose of document term matrix 
#     sX = sX.transpose()
#     sX = sX.tocsr()
#     X  = sX.toarray()


#     #Take non-zeros from y
#     inds = np.where(y)[0]
#     print 'inds: ', inds
#     if len(inds) > 1:
#         y    = y[inds]
#         #y    = 1/y
#         #print inds, y    
#     else:
#         if len(inds) == 0:
#             y    = np.zeros([1,1])
#             inds = np.array([[0]])
#         else:
#             y    = np.zeros([len(inds),1])
#             #inds = np.array([[0]])

#     #Compute estimation of weight vector (i.e. user model)
#     print 'Search thread: update_keyword_matrix: Create Xt '
#     print 'len inds', len(inds)
#     sXt   = sX[inds,:]
#     Xt    = sXt.toarray()
#     XtTXt = np.dot(Xt.T,Xt)
#     eye   = mu*np.eye(Xt.T.shape[0])

#     print 'Compute inverse'
#     A = np.dot(np.linalg.inv(np.dot(Xt.T,Xt) + eye),Xt.T)

#     print 'Compute eig. values and vecs.'
#     eigv, U = np.linalg.eig(XtTXt + eye)
#     eigv    = np.absolute(eigv)
#     idx     = np.argsort(eigv)[::-1]
#     eigv    = eigv[idx]
#     U       = U[:,idx]

#     eigvk   = 1.0/eigv
#     eigv[np.absolute(eigv)> 1/minLambda] = 0
#     k = (eigvk > 0).sum()
#     eigvkdia = np.diag(eigvk)

#     print Xt.T.shape, Xt.shape, eye.shape
#     #print dumA.shape

#     return [], []

# def return_keyword_relevance_and_variance_estimates_scinet_fast(y, mu):

#     #Parameters
#     minLambda = 0.5
#     c         = 1.0

#     #Load document term matrix 
#     sX = load_sparse_csc('data/sX.sparsemat.npz')
#     #Make transpose of document term matrix 
#     sX = sX.transpose()
#     sX = sX.tocsr()
#     X  = sX.toarray()

#     #Clusterize document term matrix
#     if not os.path.isfile('data/Xtilde.npy'):
#         Xtilde = scipy.cluster.vq.kmeans(X.T,20,iter=2,thresh=1e-01)
#         Xtilde = Xtilde[0].T
#         np.save('data/Xtilde.npy',Xtilde)
#     else:
#         Xtilde = np.load('data/Xtilde.npy')


#     #Take non-zeros from y
#     inds = np.where(y)[0]
#     print 'inds: ', inds
#     if len(inds) > 1:
#         y    = y[inds]
#         #y    = 1/y
#         #print inds, y    
#     else:
#         if len(inds) == 0:
#             y    = np.zeros([1,1])
#             inds = np.array([[0]])
#         else:
#             y    = np.zeros([len(inds),1])
#             #inds = np.array([[0]])
#     indslist = inds.tolist()


#     #Compute estimation of weight vector (i.e. user model) webmail webmail webmail 
#     print 'Search thread: update_keyword_matrix: Create Xt '
#     print 'len inds', len(inds)
#     sXt   = sX[inds,:]
#     Xt    = Xtilde[inds,:]
#     #Xt    = sXt.toarray()

#     #XtTXt = np.dot(Xt.T,Xt)
#     eye   = mu*np.eye(Xt.T.shape[0])

#     print 'Compute inverse of A'
#     A  = np.dot(np.linalg.inv(np.dot(Xt.T,Xt) + eye),Xt.T)
#     print 'Compute Atilde'
#     # Atilde  = np.linalg.inv(np.dot(X.T,X) + eye)
#     # sAtilde = sparse.csr_matrix(Atilde)
#     # print 'Compute eig. vals and vecs of A'

#     #eigvals, U = np.linalg.eigvalsh(np.dot(X.T,X) + eye)

#     # n=math.floor(0.50*sAtilde.shape[0])
#     # m=int(sAtilde.shape[0]-n)
#     # Dvec, Q = sparse.linalg.eigsh(sAtilde,k=m)
#     print A.shape

#     print 'Compute upper bound confidence:'
#     #Number of keywords
#     y_hat     = []
#     sigma_hat = []
#     s         = []
#     numkw = Xtilde.shape[0]
#     for i in range(numkw):
#         aI = np.dot(Xtilde[i,:],A)
#         #s.append(float(np.dot(aI,y)+c*np.dot(aI,aI.T)))
#         y_hat.append( float(np.dot(aI,y)) )
#         sigma_hat.append( np.dot(aI,aI.T) ) 

#         #if i in indslist:
#             #s.append(float(np.dot(aI,y)))
#         #else:
#             #s.append(float(np.dot(aI,y)+c*np.dot(aI,aI.T)))


#     #print Xt.T.shape, Xt.shape, eye.shape
#     #print dumA.shape
#     y_hat = np.array([y_hat])
#     y_hat = y_hat.T
#     sigma_hat = np.array([sigma_hat])
#     sigma_hat = sigma_hat.T

#     return y_hat, sigma_hat

# #
# def return_keyword_relevance_and_variance_estimates_scinet_fast_sparse(y, mu):

#     #Parameters
#     minLambda = 0.5
#     c         = 1000.0

#     #Load document term matrix 
#     sX = load_sparse_csc('data/sX.sparsemat.npz')
#     #Make transpose of document term matrix 
#     sX = sX.transpose()
#     sX = sX.tocsr()
#     #X  = sX.toarray()

#     #Take non-zeros from y
#     inds = np.where(y)[0]
#     print 'inds: ', inds
#     if len(inds) > 1:
#         y    = y[inds]
#         #y    = 1/y
#         #print inds, y    
#     else:
#         if len(inds) == 0:
#             y    = np.zeros([1,1])
#             inds = np.array([[0]])
#         else:
#             y    = np.zeros([len(inds),1])
#             #inds = np.array([[0]])
#     indslist = inds.tolist()
#     sy = sparse.csr_matrix(y)

#     #Compute estimation of weight vector (i.e. user model) webmail webmail webmail 
#     print 'Search thread: update_keyword_matrix: Create Xt '
#     print 'len inds', len(inds)
#     sXt   = sX[inds,:]
#     #sXtTXt = sXt.T.dot(sXt)
#     #print type(sXtTXt)
#     #seye   = mu*sparse.eye(Xt.T.shape[0])
#     speye  = mu*sparse.identity(sXt.T.shape[0])

#     print 'Compute inverse of A'
#     sA = sparse.linalg.inv(sXt.T.dot(sXt) + speye).dot(sXt.T)
#     print sA.shape

#     print 'Compute upper bound confidence:'
#     #Number of keywords
#     y_hat     = []
#     sigma_hat = []
#     s         = []
#     numkw = sX.shape[0]
#     for i in range(numkw):
#         saI = sX[i,:].dot(sA)
#         #print saI.shape
#         #print sy.shape
#         #s.append(float(np.dot(aI,y)+c*np.dot(aI,aI.T)))
#         m = saI*sy.toarray()
#         y_hat.append( float(m[0,0]) )

#         m2= saI.dot(saI.T)
#         sigma_hat.append( float(m2[0,0]) ) 

#         #if i in indslist:
#             #s.append(float(np.dot(aI,y)))
#         #else:
#             #s.append(float(np.dot(aI,y)+c*np.dot(aI,aI.T)))


#     #print Xt.T.shape, Xt.shape, eye.shape
#     #print dumA.shape
#     y_hat = np.array([y_hat])
#     y_hat = y_hat.T
#     sigma_hat = np.array([sigma_hat])
#     sigma_hat = sigma_hat.T
#     #s = np.array([s])
#     #s = s.T


#     # sum_hat = y_hat + sigma_hat
#     #return y_hat, sigma_hat
#     return y_hat, sigma_hat    




# #


# #Compute Tikhonov regularized solution for y=Xt*w (using scipy function lsqr)
# #I.e. compute estimation of user model
# def estimate_w(Xt,y):
#     #
#     mu = 0.5
#     #mu = 0.0
#     try:
#         print 'Search thread: Estimating w'
#         w = scipy.sparse.linalg.lsqr(Xt,y, damp=mu)[0]
#         #print w.shape
#     except ZeroDivisionError:
#         print 'Xt nrows: ', Xt.shape[1]
#         w = Xt.shape[1]*[0.0]
#         print w
#     return w



# #Computes cosine similarity between input vec. (test_vec) and previously
# #suggested documents and returns vector of these similarities
# def compute_relevance_scores(docinds, test_vec):

#     #Sparse tfidf matrix 
#     sX = load_sparse_csc('data/sX.sparsemat.npz')    

#     #print 'Search thread: Create Xt '
#     #print 'Search thread: X shape, ', sX.shape
#     sXcsr = sX.tocsr()
#     sXtcsr= sXcsr[docinds,:]
#     sXtcsc= sXtcsr.tocsc()
#     Xt    = sXtcsc.toarray()
#     print 'Search thread: Xt shape, ', Xt.shape

#     #Convert Xt to corpus form
#     nr, nc = Xt.shape
#     Xtlist = []
#     for i in range(nr):
#         Xtlist.append( gensim.matutils.full2sparse(Xt[i][:]) )
#         #print len(Xtlist[i])
#     #print 'Xt len:', len(Xtlist)

#     #Compute relevance scores
#     nr = len(Xtlist)
#     y = []
#     for i in range(nr):
#         y.append(gensim.matutils.cossim(test_vec,Xtlist[i]))
#         #print y[i]
#     y = np.asarray([y])
#     y = y.transpose()
#     nr, nc = y.shape

#     return y







# #
# def search_dime_linrel_summing_previous_estimates(query):
    
#     #Get current path
#     cpath  = os.getcwd()
#     print 'LinRel: ', cpath
#     #cpathd = cpath + '/' + 'data'
#     #os.chdir(cpathd)

#     #Import data
#     json_data = open('data/json_data.txt', 'r')
#     data = json.load(json_data)    

#     #Import dictionary
#     dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

#     #Open docindlist (the list of indices of suggested documents
#     f = open(cpath + '/data/docindlist.list','r')
#     docinds = pickle.load(f)
#     #Sort from smallest to largest index value
#     #docinds.sort() 
#     print 'Search thread: Old docindlist: ', docinds

#     #
#     f = open('data/varlist.list', 'r')
#     varlist = pickle.load(f)
#     nwords = varlist[0]
#     ndocuments = varlist[1]

#     #Import tfidf model by which the relevance scores are computed 
#     tfidf = models.TfidfModel.load('data/tfidfmodel.model')

#     #Make wordlist from the query string
#     test_wordlist = query.lower().split()
#     #Remove unwanted words from query
#     test_wordlist = remove_unwanted_words(test_wordlist)

#     #Convert the words into nearest dictionary word
#     for nword, word in enumerate(test_wordlist):
#         correctedword = difflib.get_close_matches(word, dictionary.values())
#         if len(correctedword):
#             test_wordlist[nword] = correctedword[0]
#         else:
#             test_wordlist[nword] = ' '
#     print "Search thread: Closest dictionary words: ", test_wordlist

#     #Make bag of word vector of the input string taken from keyboard
#     test_vec = dictionary.doc2bow(test_wordlist)

#     #
#     kws      = return_and_print_estimated_keyword_indices_and_values(test_vec, docinds, dictionary, nwords)
#     #make string of keywords 
#     kwsstr = ''
#     for i in range(len(kws)):
#         kwsstr = kwsstr + ' ' + kws[i]
#     jsons, docinds = search_dime_docsim(query)


#     #gensim.matutils.corpus2dense(corpus, num_terms, num_docs=None, dtype=<type 'numpy.float32'>)
#     #x = np.arange(0, 5, 0.1);
#     #y = np.sin(x)

#     #Convert to tfidf vec (list of 2-tuples, (word id, tfidf value))
#     test_vec = tfidf[test_vec] 
#     test_vec_full = twotuplelist2fulllist(test_vec, nwords)
#     #plt.plot(range(len(test_vec_full)), test_vec_full)
#     #plt.show()

#     #Compute relevance scores 
#     #nr, nc = Xt.shape
#     nc = len(docinds)
#     if nc == 0:
#         jsons, docinds = search_dime_docsim(query)
#         docindsunsorted = docinds
#         docinds.sort()
#         print 'DocSim suggested inds: ', docinds
#         #docinds.sort()
#         cpath = os.getcwd()
#         cpath = cpath + '/' + 'data'
#         #os.chdir(cpath)
#         update_Xt_and_docindlist(docinds)
#         #os.chdir('../')
#         y = compute_relevance_scores(docinds, test_vec)
#     else:        
#         #docinds.sort()
#         y = compute_relevance_scores(docinds, test_vec)

#     #
#     print 'Search thread: length of relevance score vec (y): ', y.shape
#     #print 'Search thread: Relevance scores: ', y

#     #Normalize y vector
#     ysum = y.sum()
#     if ysum > 0:
#         y = y/ysum

#     #
#     sy = sparse.csc_matrix(y)

#     #
#     sA = update_A(docinds, y)
#     sy_hat = sA*sy
#     y_hat  = sy_hat.toarray()
#     #print 'shape of y_hat', y_hat.shape

#     cpath = os.getcwd()
#     cpath = cpath + '/data'
#     if os.path.isfile(cpath):
#         print "Search thread: updating y_hat" 
#         y_hat_prev = np.load('data/y_hat_prev.npy')
#         if len(y_hat) == len(y_hat_prev):
#             print 'Search thread: update y_hat (by y_hat = y_hat + y_hat_prev)'
#             y_hat = y_hat + y_hat_prev
#         #Normalize y_hat
#         y_hat_sum = y_hat.sum()
#         if y_hat_sum > 0:
#             y_hat = y_hat/y_hat_sum
#         #
#         #os.chdir(cpath)
#         np.save(cpath + '/y_hat_prev.npy', y_hat)
#         #os.chdir('../')
#     else:
#         #Normalize y_hat
#         y_hat_sum = y_hat.sum()
#         if y_hat_sum > 0:
#             y_hat = y_hat/y_hat_sum        
#         print "Search thread: Saving y_hat first time"
#         #os.chdir(cpath)
#         np.save(cpath + '/y_hat_prev.npy', y_hat)
#         #os.chdir('../')        
#         #np.save(cpathd + '/y_hat_prev.npy', y_hat)

#     #
#     print 'Search thread: y_hat max:', y_hat.max(), 'y_hat argmax:', y_hat.argmax()

#     #Compute upper bound on the deviation of the relevance estimate using matrix A
#     sigma_hat = np.sqrt(sA.multiply(sA).sum(1)) 
#     sigma_hat = np.array(sigma_hat)

#     print 'Search thread: sigma_hat max:', sigma_hat.max(), ', sigma_hat argmax: ', sigma_hat.argmax()


#     #Coefficient determining the importance of deviation of the relevance vector
#     #in search
#     c = 0.0

#     #Compute doc. indices
#     if sigma_hat.max() == 0:
#         print "Search thread: LinRel don't suggest anything, use DocSim"
#         docs, docinds = search_dime_docsim(query)
#         #docinds.sort()
#         #pass
#     else: 
#         #
#         #print 'shape y_hat,', y_hat.shape, 'type: ', type(y_hat)
#         #print 'shape sigma_hat,', sigma_hat.shape, 'type: ', type(sigma_hat)
#         e = np.array(y_hat + (c/2)*sigma_hat)
#         #print e
#         #print 'e shape,', e.shape
#         print 'Search thread: e max:', e.max(), 'e argmax:', e.argmax()
#         #print e.shape

#         docinds= np.argsort(e[:,0])
#         docinds= docinds[-20:]
#         docinds= docinds.tolist()
#         #print docinds
#     #print type(docinds)
#     #print docinds
#     #docinds.sort()
#     #print 'Search thread: New docindlist: ', docinds


#     #Get jsons
#     jsons = []
#     for i in range(len(docinds)):
#         #print docinds[i]
#         jsons.append(data[docinds[i]])

#     docinds.sort()
#     cpath = os.getcwd()
#     #os.chdir(cpath + '/data')
#     update_Xt_and_docindlist(docinds)
#     #os.chdir('../')

#     return jsons[-20:], kws




# #Updates LinRel matrix, denoted by A 
# def return_keyword_relevance_estimates(docinds, y):

#     #Load sparse tfidf matrix
#     #sX = np.load('sX.npy')
#     sX = load_sparse_csc('data/sX.sparsemat.npz')

#     print "Search thread: update_keyword_matrix: Updating A"

#     #Compute estimation of weight vector (i.e. user model)
#     print 'Search thread: update_keyword_matrix: Create Xt '
#     sXcsr = sX.tocsr()
#     sXcsr = sX
#     print 'Search thread: Type of sXcsr: ', type(sXcsr)
#     Xt    = sXcsr.toarray()
#     Xt    = sXcsr

#     #TRANSPOSE!!
#     Xt    = Xt.transpose()

#     print 'Search thread: update_keyword_matrix: Xt shape: ', Xt.shape, ' type: ', type(Xt)
#     print 'Search thread: update_keyword_matrix: min val Xt: ', Xt.min()

#     print 'Search thread: update_keyword_matrix: y shape: ', y.shape
#     #
#     w_hat = estimate_w(Xt,y)
#     w_hat = np.array([w_hat])
#     w_hat = w_hat.transpose()

#     print 'Search thread: update_keyword_matrix: w shape: ', w_hat.shape, ' type: ', type(w_hat)
#     #r_hat = np.dot(Xt,w_hat)
#     r_hat = Xt*w_hat
#     print 'Search thread: update_keyword_matrix: r_hat shape: ', r_hat.shape, ' type: ', type(r_hat)
#     print 'Search thread: update_keyword_matrix: max val r_hat: ', r_hat.max()
#     return r_hat

# #
# def search_dime_linrel_without_summing_previous_estimates(query):
#     #print 'NEGLECTING HISTORY!!!'

#     #Get current path
#     cpath  = os.getcwd()
#     print 'LinRel: ', cpath
#     #cpathd = cpath + '/' + 'data'
#     #os.chdir(cpathd)

#     #Import data
#     json_data = open('data/json_data.txt', 'r')
#     data = json.load(json_data)    

#     #Import dictionary
#     dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

#     #Open docindlist (the list of indices of suggested documents
#     f = open(cpath + '/data/docindlist.list','r')
#     docinds = pickle.load(f)
#     #Sort from smallest to largest index value
#     #docinds.sort() 
#     print 'Search thread: Old docindlist: ', docinds

#     #
#     f = open('data/varlist.list', 'r')
#     varlist = pickle.load(f)
#     nwords = varlist[0]
#     ndocuments = varlist[1]

#     #Import tfidf model by which the relevance scores are computed 
#     tfidf = models.TfidfModel.load('data/tfidfmodel.model')

#     #Make wordlist from the query string
#     test_wordlist = query.lower().split()

#     #Remove unwanted words from query
#     test_wordlist = remove_unwanted_words(test_wordlist)

#     #Convert the words into nearest dictionary word
#     for nword, word in enumerate(test_wordlist):
#         correctedword = difflib.get_close_matches(word, dictionary.values())
#         if len(correctedword):
#             test_wordlist[nword] = correctedword[0]
#         else:
#             test_wordlist[nword] = ' '
#     print "Search thread: Corrected words (dictionary words): ", test_wordlist
#     test_vec = dictionary.doc2bow(test_wordlist)
#     #Convert to tfidf vec (list of 2-tuples, (word id, tfidf value))
#     test_vec = tfidf[test_vec] 

#     #Compute relevance scores 
#     #nr, nc = Xt.shape
#     nc = len(docinds)
#     if nc == 0:
#         jsons, docinds = search_dime_docsim(query)
#         docindsunsorted = docinds
#         docinds.sort()
#         print 'DocSim suggested inds: ', docinds
#         #docinds.sort()
#         cpath = os.getcwd()
#         cpath = cpath + '/' + 'data'
#         #os.chdir(cpath)
#         update_Xt_and_docindlist(docinds)
#         #os.chdir('../')
#         y = compute_relevance_scores(docinds, test_vec)
#     else:        
#         #docinds.sort()
#         y = compute_relevance_scores(docinds, test_vec)

#     #
#     print 'Search thread: length of relevance score vec (y): ', y.shape
#     print 'Search thread: Relevance scores: ', y

#     #Normalize y vector
#     ysum = y.sum()
#     if ysum > 0:
#         y = y/ysum

#     #
#     sy = sparse.csc_matrix(y)

#     #
#     sA = update_A(docinds, y)
#     sy_hat = sA*sy
#     y_hat  = sy_hat.toarray()
#     #print 'shape of y_hat', y_hat.shape

#     cpath = os.getcwd()
#     cpath = cpath + '/data'
#     if os.path.isfile(cpath):
#         print "Search thread: updating y_hat" 
#         y_hat_prev = np.load('data/y_hat_prev.npy')
#         if len(y_hat) == len(y_hat_prev):
#             print 'Search thread: update y_hat (by y_hat = y_hat + y_hat_prev)'
#             y_hat = y_hat + y_hat_prev
#         #Normalize y_hat
#         y_hat_sum = y_hat.sum()
#         if y_hat_sum > 0:
#             y_hat = y_hat/y_hat_sum
#         #
#         #os.chdir(cpath)
#         np.save(cpath + '/y_hat_prev.npy', y_hat)
#         #os.chdir('../')
#     else:
#         #Normalize y_hat
#         y_hat_sum = y_hat.sum()
#         if y_hat_sum > 0:
#             y_hat = y_hat/y_hat_sum        
#         print "Search thread: Saving y_hat first time"
#         #os.chdir(cpath)
#         np.save(cpath + '/y_hat_prev.npy', y_hat)
#         #os.chdir('../')        
#         #np.save(cpathd + '/y_hat_prev.npy', y_hat)

#     #
#     print 'Search thread: y_hat max:', y_hat.max(), 'y_hat argmax:', y_hat.argmax()

#     #Compute upper bound on the deviation of the relevance estimate using matrix A
#     sigma_hat = np.sqrt(sA.multiply(sA).sum(1)) 
#     sigma_hat = np.array(sigma_hat)

#     print 'Search thread: sigma_hat max:', sigma_hat.max(), ', sigma_hat argmax: ', sigma_hat.argmax()


#     #Coefficient determining the importance of deviation of the relevance vector
#     #in search
#     c = 0.0

#     #Compute doc. indices
#     if sigma_hat.max() == 0:
#         print "Search thread: LinRel don't suggest anything, use DocSim"
#         docs, docinds = search_dime_docsim(query)
#         #docinds.sort()
#         #pass
#     else: 
#         #
#         #print 'shape y_hat,', y_hat.shape, 'type: ', type(y_hat)
#         #print 'shape sigma_hat,', sigma_hat.shape, 'type: ', type(sigma_hat)
#         e = np.array(y_hat + (c/2)*sigma_hat)
#         #print e
#         #print 'e shape,', e.shape
#         print 'Search thread: e max:', e.max(), 'e argmax:', e.argmax()
#         #print e.shape

#         docinds= np.argsort(e[:,0])
#         docinds= docinds[-20:]
#         docinds= docinds.tolist()

#     #Get jsons
#     jsons = []
#     for i in range(len(docinds)):
#         #print docinds[i]
#         jsons.append(data[docinds[i]])

#     docinds.sort()
#     cpath = os.getcwd()
#     #os.chdir(cpath + '/data')
#     update_Xt_and_docindlist(docinds)
#     #os.chdir('../')

#     return jsons[-20:]








#
# def search_dime_lda(query):

#     # Read list of forbidden words #
#     f = open('stopwordlist.list', 'r')
#     stoplist = pickle.load(f)

#     #Import data
#     json_data = open('json_data.txt')
#     data = json.load(json_data)

#     #Import dictionary
#     dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

#     #Import lda model
#     ldamodel = models.LdaModel.load('/tmp/tmpldamodel')

#     #Import document term matrix
#     f = open('doctm.data','r')
#     doctm = pickle.load(f)

#     #Number of documents
#     ndocuments = len(doctm)
    
#     #Make wordlist from the query string
#     test_wordlist = query.lower().split()
#     print test_wordlist
#     #Remove words belonging to stoplist
#     test_wordlist = remove_unwanted_words(test_wordlist, stoplist)
#     print test_wordlist


#     #Convert the words into nearest dictionary word
#     for nword, word in enumerate(test_wordlist):
#         correctedword = difflib.get_close_matches(word, dictionary.values())
#         if len(correctedword):
#             test_wordlist[nword] = correctedword[0]
#         else:
#             test_wordlist[nword] = ' '
#     print "Closest dictionary words: ", test_wordlist

#     # Convert the wordlist into bag of words (bow)
#     test_vec = dictionary.doc2bow(test_wordlist)

#     # Compute cluster (topic) probabilities
#     test_lda  = ldamodel[test_vec]

#     #Compute the topic index of the test document (query)
#     dumtidv = []
#     dumtpv  = []
#     for j in range(len(test_lda)):
#         dumtidv.append(test_lda[j][0])
#         dumtpv.append(test_lda[j][1])
#     #
#     ttid = dumtidv[np.argmax(dumtpv)]

#     #Show the words included in the topic
#     #prkw = ldamodel.show_topic(ttid, topn=10)
#     prkw = ldamodel.show_topic(ttid)

#     #Print ten keywords 
#     for i in range(len(prkw)):
#         print prkw[i][1]
 
#     #Compute topic ids for visited resources (web-pages, docs, emails, etc..)
#     dtid = []
#     for i in range(len(doctm)):
#         dumtidv = []
#         dumtpv  = []
#         doc_lda = ldamodel[doctm[i]]
#         for j in range(len(doc_lda)):
#                 dumtidv.append(doc_lda[j][0])
#                 dumtpv.append(doc_lda[j][1])
#         dtid.append(dumtidv[np.argmax(dumtpv)])
#     #
#     dtid = np.array(dtid)

#     # Give uri of documents that are in cluster of index ttid (in the same cluster as the test document)
#     docinds = np.where(dtid == ttid)[0]

#     #Return the json objects that are in the same
#     #cluster
#     jsons = []
#     for i in range(len(docinds)):
#         #print docinds[i]
#         jsons.append(data[docinds[i]])
    
#     print len(jsons)
    
#     return jsons[0:5]





# #Search using gensim's cossim-function (cosine similarity)
# def search_dime_docsim_old(query):

#     #Get current path
#     cpath  = os.getcwd()
#     cpathd = cpath + '/' + 'data'
#     if os.path.exists(cpathd):
#         pass
#         #os.chdir(cpathd)
#     else:
#         check_update()
#         #os.chdir(cpathd)

#     #Import data
#     json_data = open('data/json_data.txt')
#     data = json.load(json_data)

#     #Load index into which the query is compared
#     if os.path.isfile('/tmp/similarityvec'):
#         index = similarities.docsim.Similarity.load('/tmp/similarityvec')
#     else:
#         update_docsim_model()
#         index = similarities.docsim.Similarity.load('/tmp/similarityvec')

#     #Import dictionary
#     dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

#     #
#     f = open('data/varlist.list','r')
#     varlist = pickle.load(f)
#     nword = varlist[0]
#     ndocuments = varlist[1]

#     #
#     if os.path.isfile('data/docindlist.list'):
#         f = open('data/docindlist.list','r')
#         docinds = pickle.load(f)
#     else:
#         #os.chdir(cpathd)
#         update_Xt_and_docindlist([0])
#         #os.chdir('../')
#         f = open('data/docindlist.list','r')
#         docinds = pickle.load(f)

    
#     #Import document term matrix
#     f = open('data/doctm.data','r')
#     doctm = pickle.load(f)

#     #Make wordlist from the query string
#     test_wordlist = query.lower().split()

#     #Remove words belonging to stoplist
#     test_wordlist = remove_unwanted_words(test_wordlist)

#     #Convert the words into nearest dictionary word
#     for nword, word in enumerate(test_wordlist):
#         correctedword = difflib.get_close_matches(word, dictionary.values())
#         if len(correctedword):
#             test_wordlist[nword] = correctedword[0]
#         else:
#             test_wordlist[nword] = ' '
#     print "Search thread: Closest dictionary words: ", test_wordlist

#     # Convert the wordlist into bag of words (bow) representation
#     test_vec = dictionary.doc2bow(test_wordlist)

#     #Find the indices of most similar documents
#     doclist = index[test_vec]
#     #print 'Search thread: docinds of DocSim: ', doclist

#     #Take indices of similar documents
#     docinds = []
#     for i, d in enumerate(doclist):
#         docinds.append(doclist[i][0])

#     #
#     jsons = []
#     for i in range(len(docinds)):
#         #print docinds[i]
#         jsons.append(data[docinds[i]])
    
#     # print len(jsons)   
#     return jsons[0:20], docinds[0:20]

