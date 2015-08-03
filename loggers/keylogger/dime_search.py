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


#
def search_dime_linrel_without_summing_previous_estimates(query):

    #Import data
    json_data = open('json_data.txt')
    data = json.load(json_data)    

    #Import dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

    #Open docindlist (the list of indices of suggested documents)
    f = open('docindlist.list','r')
    docinds = pickle.load(f)
    #Sort from smallest to largest index value
    docinds.sort()
    print 'Search thread: Old docindlist: ', docinds

    #
    f = open('varlist.list', 'r')
    varlist = pickle.load(f)
    nwords = varlist[0]
    ndocuments = varlist[1]

    #Import tfidf model by which the relevance scores are computed 
    tfidf = models.TfidfModel.load('tfidfmodel.model')

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
        docinds.sort()
        os.chdir(cpath + '/data')
        update_Xt_and_docindlist(docinds)
        os.chdir('../')
        y  = compute_relevance_scores(docinds, test_vec)
    else:        
        docinds.sort()
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
    
    if os.path.isfile('y_hat_prev.npy'):
        print "Search thread: updating y_hat" 
        y_hat_prev = np.load('y_hat_prev.npy')
        if len(y_hat) == len(y_hat_prev):
            print 'Search thread: update y_hat (by y_hat = y_hat + y_hat_prev)'
            y_hat = y_hat + y_hat_prev
        #Normalize y_hat
        y_hat_sum = y_hat.sum()
        if y_hat_sum > 0:
            y_hat = y_hat/y_hat_sum
        np.save('y_hat_prev.npy', y_hat)
    else:
        #Normalize y_hat
        y_hat_sum = y_hat.sum()
        if y_hat_sum > 0:
            y_hat = y_hat/y_hat_sum        
        print "Search thread: Saving y_hat first time"
        np.save('y_hat_prev.npy', y_hat)

    #
    print 'Search thread: y_hat max:', y_hat.max(), 'y_hat argmax:', y_hat.argmax()

    #Compute upper bound on the deviation of the relevance estimate using matrix A
    sigma_hat = np.sqrt(sA.multiply(sA).sum(1)) 
    sigma_hat = np.array(sigma_hat)

    print 'Search thread: sigma_hat max:', sigma_hat.max(), ', sigma_hat argmax: ', sigma_hat.argmax()


    #Coefficient determining the importance of deviation of the relevance vector
    #in search
    c = 1.5

    #Compute doc. indices
    if sigma_hat.max() == 0:
        print "Search thread: LinRel don't suggest anything, use DocSim"
        docs, docinds = search_dime_docsim(query)
        docinds.sort()
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
    docinds.sort()
    #print 'Search thread: New docindlist: ', docinds
    os.chdir(cpath + '/data')
    update_Xt_and_docindlist(docinds)
    os.chdir('../')

    #print docinds
    jsons = []
    for i in range(len(docinds)):
        #print docinds[i]
        jsons.append(data[docinds[i]])

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



# def search_dime_linrel(query):

#     #Import data
#     json_data = open('json_data.txt')
#     data = json.load(json_data)    

#     #Import dictionary
#     dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
    
#     #Import lda model
#     #ldamodel = models.LdaModel.load('/tmp/tmpldamodel')
    
#     #Import A matrix needed in LinRel
#     A = np.load('A.npy')
#     print 'A shape:', A.shape

#     #Import Xt
#     if os.path.isfile('Xt.npy'):
#         Xt = np.load('Xt.npy')
#     else:
#         Xt = np.array([[]])
#     #Xt  = Xt.transpose()
#     nr, nc = Xt.shape
#     print 'Xt shape:', Xt.shape

#     #Import document term matrix in full form
#     X  = np.load('X.npy')
    
#     #Import doctm
#     f = open('doctm.data','r')
#     doctm = pickle.load(f)

#     #Learn tfidf model from the document term matrix
#     tfidf = models.TfidfModel(doctm)

#     # Read list of forbidden words #
#     s1 = open('stop-words/stop-words_english_1_en.txt','r')
#     s2 = open('stop-words/stop-words_english_2_en.txt','r')
#     s3 = open('stop-words/stop-words_english_3_en.txt','r')
#     s4 = open('stop-words/stop-words_finnish_1_fi.txt','r')
#     s5 = open('stop-words/stop-words_finnish_2_fi.txt','r')
#     sstr1=s1.read()
#     sstr2=s2.read()
#     sstr3=s3.read()
#     sstr4=s4.read()
#     sstr5=s5.read()
#     #
#     sstr  = sstr1 + sstr2 + sstr3 + sstr4 + sstr5
#     #Create list of forbidden words
#     stoplist = set(sstr.split())

#     #Number of documents
#     ndocuments = len(doctm)
#     #Number of words
#     nwords = len(dictionary)

#     #print 'Number of documents ' + str(ndocuments)

#     #Make wordlist from the query string
#     test_wordlist = query.lower().split()
#     #Remove unwanted words from query
#     test_wordlist = remove_unwanted_words(test_wordlist, stoplist)

#     #Convert the words into nearest dictionary word
#     for nword, word in enumerate(test_wordlist):
#         correctedword = difflib.get_close_matches(word, dictionary.values())
#         if len(correctedword):
#             test_wordlist[nword] = correctedword[0]
#         else:
#             test_wordlist[nword] = ' '
#     print "Closest dictionary words: ", test_wordlist
#     test_vec = dictionary.doc2bow(test_wordlist)
#     #Convert to sparse tfidf vec
#     test_vec = tfidf[test_vec]

#     #Compute relevance scores 
#     nr, nc = Xt.shape
#     if nc == 0:
#         jsons, docinds = search_dime_docsim(query)
#         Xt = update_Xt_and_docindlist(docinds)
#         y  = compute_relevance_scores(test_vec, Xt)
#     else:        
#         y = compute_relevance_scores(test_vec, Xt)
#     #Normalize y vector
#     ysum = y.sum()
#     if ysum > 0:
#         y = y/ysum
#     #print y
#     #print y.sum()
#     #print 'y:', y.shape

#     #Open docindlist (the list of indices of suggested documents)
#     f = open('docindlist.list','r')
#     docindl = pickle.load(f)
#     A = update_A(X, Xt, y)
#     print 'A: ', A.shape
#     y_hat = np.dot(A,y)
    
#     if os.path.isfile('y_hat_prev.npy'):
#         y_hat_prev = np.load('y_hat_prev.npy')
#         print 'size', y_hat_prev.shape
#         vals = y_hat_prev[docindl]
#         print 'size', vals.shape
#         vals = vals.tolist()
#         np.put(y_hat, docindl, vals)
#     else:
#         np.save('y_hat_prev.npy', y_hat)

#     print 'y_hat max:', y_hat.max(), 'y_hat argmax:', y_hat.argmax()
#     #Compute upper bound on the deviation of the relevance estimate using matrix A
#     #The effect of upper bound
#     c  = 1.05
#     sigma_hat = np.array([np.linalg.norm(A, axis = 1)])
#     sigma_hat = sigma_hat.transpose()
#     sigma_hat = (c/2)*sigma_hat
#     #print 'sigma_hat:', sigma_hat
#     print 'sigma_hat max:', sigma_hat.max(), ', sigma_hat argmax: ', sigma_hat.argmax()


#     #Compute doc. indices
#     if sigma_hat.max() == 0:
#         jsons, docinds = search_dime_docsim(query)
#         print 'Doc inds:', docinds
#     else:
#         #
#         e = y_hat + (c/2)*sigma_hat
#         print 'e max:', e.max(), 'e argmax:', e.argmax()
#         #print e.shape

#         #Take indices corresponding to ten
#         #largest values of vector e
#         #docinds= np.argpartition(e[:,0], -4)[-10:]
#         docinds= np.argsort(e[:,0])
#         docinds= docinds[-10:]
#         docinds= docinds.tolist()

#     update_Xt_and_docindlist(docinds)

#     print docinds
#     #update_A()
#     jsons = []
#     for i in range(len(docinds)):
#         #print docinds[i]
#         jsons.append(data[docinds[i]])

#     return jsons[-5:]




# def search_dime_lda2(data, doctm, ldamodel, dictionary, query):

#         #Make wordlist from the query string
#         test_wordlist = query.lower().split()
#         #
#         test_vec = dictionary.doc2bow(test_wordlist)
#         #
#         test_lda  = ldamodel[test_vec]

#         #Compute the topic index of the test document
#         dumtidv = []
#         dumtpv  = []
#         for j in range(len(test_lda)):
#             dumtidv.append(test_lda[j][0])
#             dumtpv.append(test_lda[j][1])
#         #The topic index of the test document
#         ttid = dumtidv[np.argmax(dumtpv)]

#         #Compute topic ids for documents
#         dtid = []
#         for i in range(len(doctm)):
#             dumtidv = []
#             dumtpv  = []
#             doc_lda = ldamodel[doctm[i]]
#             for j in range(len(doc_lda)):
#                     dumtidv.append(doc_lda[j][0])
#                     dumtpv.append(doc_lda[j][1])
#             dtid.append(dumtidv[np.argmax(dumtpv)])

#         dtid = np.array(dtid)

#         # Give json objects corresponding documents that are in cluster ttid (in the same cluster as test doc.)

#         #Take indices of the corresponding json objects
#         docinds = np.where(dtid == ttid)[0]

#         #Return the json objects that are in the same
#         #cluster (i.e. topic)
#         jsons = []
#         for i in range(len(docinds)):
#             #print docinds[i]
#             jsons.append(data[docinds[i]])

#         return jsons[0:5], docinds[0:5]



