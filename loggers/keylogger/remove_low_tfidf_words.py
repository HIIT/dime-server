#Remove words having small tfidf value#!/usr/bin/python
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
import matplotlib.pyplot as plt

#
import os

#
from update_dict_lda_and_Am import *

def remove_low_tfidf_words():
    #Import data
    if os.path.isfile('data/sX.sparsemat.npz'):
        sX = load_sparse_csc('data/sX.sparsemat.npz')
    else:
        print "no X!"

    #
    print "shape of X", sX.shape
    tfidf_values = sX.sum(0)
    tfidf_values = np.array(tfidf_values)
    tfidf_values = tfidf_values.T

    #

    #Take indices of words having tfidf value larger than 1
    boolvec = tfidf_values < 1.0
    inds    = np.where(boolvec == True)[0]

    #Modify dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
    #Print words 
    for k in inds:
        print dictionary.get(k)

    #Remove bad words from dictionary (i.e. words having tfidf < 1)
    dictionary.filter_tokens(bad_ids = inds)
    #Assign new word ids to all words after filtering.
    dictionary.compactify()
    #Save the updated version
    dictionary.save('/tmp/tmpdict.dict')

    #
    update_doctm('data/')
    update_doc_tfidf_list('data/')
    update_docsim_model()
    update_Xt_and_docindlist([0])
    update_tfidf_model('data/')
    create_stopwordlist('data/')
    
    #plt.plot(tfidf_values[kwinds])
    plt.plot(tfidf_values[inds])
    plt.show()

 

#
def take_low_df_words():
    #Import data
    if os.path.isfile('data/sXdoctm.sparsemat.npz'):
        sX = load_sparse_csc('data/sXdoctm.sparsemat.npz')
    else:
        print "no X!"

    #Modify dictionary
    dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')

    #Number of documents
    N = sX.shape[0]
    N = float(N)

    #O = word occurrence matrix, (0,1) - matrix
    boolmat = sX > 0
    boolmat = boolmat.tolil()
    #Create zero sparse matrix
    O = scipy.sparse.lil_matrix(np.zeros(sX.shape))
    O[boolmat] = 1.0
    O = O.tocsc()
    print type(O), O.shape, O.max()

    #
    print "shape of X", sX.shape
    df_values = O.sum(0)
    df_values = np.array(df_values)
    df_values = df_values.T

    #Take indices of words having 1 < tf < N/10, where N = num. of docs
    #N = 100
    c = 0.9
    boolvec= np.logical_or(df_values <= 1, df_values >= (c*N))
    #boolvec = df_values >= (c*N)
    
    #print boolvec
    inds    = np.where(boolvec == True)[0]

    #Remove bad words from dictionary (i.e. words having tfidf < 1)
    dictionary.filter_tokens(bad_ids = inds)
    #Assign new word ids to all words after filtering.
    dictionary.compactify()
    #Save the updated version
    dictionary.save('/tmp/tmpdict.dict')    

    #
    update_doctm('data/')
    update_doc_tfidf_list('data/')
    update_docsim_model()
    update_Xt_and_docindlist([0])
    update_tfidf_model('data/')
    create_stopwordlist('data/')

    #plt.plot(df_values[inds])
    #plt.show()
    #
    return inds


if __name__ == "__main__":    
    #remove_low_tfidf_words()
    inds = take_low_df_words()