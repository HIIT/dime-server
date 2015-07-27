
import os, os.path, codecs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
import numpy as np
import math
import os, os.path, codecs
from textblob import TextBlob as tb
import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
from classes import *


#current_user = pickle.load( open( "current_user_1.p", "rb" ) )
import numpy

def tf(word, wordList):
    #print word
    #print float(wordList.count(word))
    #print len(wordList)
    return float(wordList.count(word)) / len(wordList)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)
 
def idf(word, bloblist):
    #print word
    #print (1 + n_containing(word, bloblist))
    #print math.log(float(len(bloblist)) / (1 + n_containing(word, bloblist)))
    #print float(len(bloblist)) / (1 + n_containing(word, bloblist))
    return math.log(float(len(bloblist)) / (1 + n_containing(word, bloblist)))
 

def tfidf(word, blob, bloblist):
    #print word
    #print tf(word, blob) * idf(word, bloblist)
    return tf(word, blob) * idf(word, bloblist)


def getTopWordsTF(blob,bloblist,k):
    scores = {word: tf(word, blob) for word in blob}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    topWords = []
    for word, score in sorted_words[:k]:
        new = []
        new.append(word)
        new.append(round(score, 5))
        topWords.append(new)
        #print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
    return topWords
def getTopPhrases_list(current_user, peer_id):
    print'TF top words for:', peer_id
    print "###########getTopPhrases('peer', 'user', True)"
    getTopPhrases(current_user,'peer', 'user', True, peer_id)

    print "###########getTopPhrases('peer', 'peer', True)"
    getTopPhrases(current_user,'peer', 'peer', True, peer_id)

    print "###########getTopPhrases('peer', 'both', True)"
    getTopPhrases(current_user,'peer', 'both', True, peer_id)

    print "###########getTopPhrases('thread', 'user', True)"
    getTopPhrases(current_user,'thread', 'user', True, peer_id)

    print "###########getTopPhrases('thread', 'peer', True)"
    getTopPhrases(current_user,'thread', 'peer', True, peer_id)

    print "###########getTopPhrases('thread', 'both', True)"
    getTopPhrases(current_user,'thread', 'both', True, peer_id)

    print "###########getTopPhrases('thread', 'user', False)"
    getTopPhrases(current_user,'thread', 'user', False, peer_id)

    print "###########getTopPhrases('thread', 'peer', False)"
    getTopPhrases(current_user,'thread', 'peer', False, peer_id)

    print "###########getTopPhrases('thread', 'both', False)"
    getTopPhrases(current_user,'thread', 'both', False, peer_id)
    
def getTopPhrases(current_user, level, p, doc_list_flag, peer_id):
    # doc_list_flag indicates whether the list must be initialised just once or must be initialised for every peer
    # doc_list_flag = True then doc_list is initialised for every peer.
    if (level =='peer'):
        doc_list = []
        for inter in current_user.peer_list:
            doc_list.append(inter.getPhrase(p))
        for inter in current_user.peer_list:
            if(not inter.email ==peer_id):
                continue
            #print inter.email
            #print inter.getPhrase(p)
            #print doc_list
            print getTopWordsTF(inter.getPhrase(p),doc_list,10)
            print '\n'
    elif (level =='thread'):
        doc_list = [] 
        if(doc_list_flag):
            for inter in current_user.peer_list:
                doc_list= []
                if(not inter.email ==peer_id):
                    continue
                print inter.email
                for thread in inter.thread_list:
                    doc_list.append(thread.getPhrase(p))
                for thread in inter.thread_list:
                    print thread.subject, len(thread.email_list)
                    print getTopWordsTF(thread.getPhrase(p),doc_list,10)
                    print '\n'
        else:
            doc_list= []
            for inter in current_user.peer_list:
                for thread in inter.thread_list:
                    doc_list.append(thread.getPhrase(p))
            for inter in current_user.peer_list:
                if(not inter.email ==peer_id):
                    continue
                for thread in inter.thread_list:
                    print thread.subject, len(thread.email_list)
                    print getTopWordsTF(thread.getPhrase(p),doc_list,10)
                    print '\n'
    

def topPhrases_NMF(current_user):
    phrases = set()
    print 'Topic Modelling with NMF'
    for inter in current_user.peer_list:
        l = inter.getPhrase('both')
        for phrase in l:
            phrases.add(phrase)
    phrases = list(phrases)
    doc_list = []
    p = 'both'
    subject_list = []
    _peer_list = []
    for inter in current_user.peer_list:
        for thread in inter.thread_list:
            subject_list.append(thread.subject)
            _peer_list.append(inter.email)
            doc_list.append(thread.getPhrase(p))
    m = len(phrases)
    n = len(doc_list)
    a = numpy.zeros(shape=(n,m))
    for i in range(n):
        doc = doc_list[i]
        for phrase in doc:
            j = phrases.index(phrase)
            val = tf(phrase, doc) 
            a[i,j] = val
          
    model = decomposition.NMF(init="nndsvd", n_components=20, max_iter=500)
    W = model.fit_transform(a)
    H = model.components_	
    for topic_index in range( H.shape[0] ):
        top_indices = np.argsort( H[topic_index,:] )[::-1][0:10]
        term_ranking = [phrases[i] for i in top_indices]
        print "Topic %d: %s" % ( topic_index, ",".join( term_ranking ) )

    topics = {}
    for i in range(len(subject_list)):
        topic = np.argmax(W[i, :])
        if( _peer_list[i] not in topics):
            topics[_peer_list[i]] = set([topic])
        else :
            topics[_peer_list[i]].add(topic)
    print topics

