# -*- coding: iso-8859-15 -*-
import os, os.path, codecs
import numpy as np
import math
import os, os.path, codecs
from textblob import TextBlob as tb
import string
import re
from classes import *


#current_user = pickle.load( open( "current_user_1.p", "rb" ) )
import numpy
pattern = re.compile('[\W_]+')
import string
ex_stop_words = ['thanks', 'cheers', 'm.s']

def getPhrases(text, stop_text):
    text = re.sub(u"(\u2018|\u2019)", " ", text)
    np = tb(text).noun_phrases
    ret = []
    for t in np:
        temp = ' '.join([word for word,pos in tb(t).tags if pos in ('NNP','NNS','NN','NNPS') and word not in set(string.punctuation) and word not in stop_text and word not in ex_stop_words])
        #temp = t
        if (temp not in(' ', '')):
            ret.append(temp)
    return ret
    
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

def getTopPhrases_list(current_user, i_peer_list, file):
    file.write('\nTF top words for:'+str( i_peer_list))
    file.write( "\n###########getTopPhrases('peer', 'user', True)")
    getTopPhrases(current_user,'peer', 'user', True, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('peer', 'peer', True)")
    getTopPhrases(current_user,'peer', 'peer', True, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('peer', 'both', True)")
    getTopPhrases(current_user,'peer', 'both', True, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('thread', 'user', True)")
    getTopPhrases(current_user,'thread', 'user', True, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('thread', 'peer', True)")
    getTopPhrases(current_user,'thread', 'peer', True, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('thread', 'both', True)")
    getTopPhrases(current_user,'thread', 'both', True, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('thread', 'user', False)")
    getTopPhrases(current_user,'thread', 'user', False, i_peer_list, file)

    file.write( "\n###########getTopPhrases('thread', 'peer', False)")
    getTopPhrases(current_user,'thread', 'peer', False, i_peer_list, file)
    
    file.write( "\n###########getTopPhrases('thread', 'both', False)")
    getTopPhrases(current_user,'thread', 'both', False, i_peer_list, file)
    
def getTopPhrases(current_user, level, p, doc_list_flag, i_peer_list, file):
    # doc_list_flag indicates whether the list must be initialised just once or must be initialised for every peer
    # doc_list_flag = True then doc_list is initialised for every peer.
    
    if (level =='peer'):
        doc_list = []
        for inter in current_user.peer_list:
            doc_list.append(inter.getPhrase(p))
        for inter in current_user.peer_list:
            if(inter.email not in i_peer_list):
                continue
            file.write('\n')
            file.write('\n')
            file.write(inter.email)
            #print inter.getPhrase(p)
            #print doc_list
            file.write('\n')
            file.write(str(getTopWordsTF(inter.getPhrase(p),doc_list,10)))
    elif (level =='thread'):
        doc_list = [] 
        if(doc_list_flag):
            for inter in current_user.peer_list:
                doc_list= []
                if(inter.email not in i_peer_list):
                    continue
                file.write(inter.email)
                for thread in inter.thread_list:
                    doc_list.append(thread.getPhrase(p))
                for thread in inter.thread_list:
                    file.write('\n')
                    file.write('\n')
                    file.write(str(thread.subject) +'  '+str(len(thread.email_list)))
                    file.write('\n')
                    file.write(str(getTopWordsTF(thread.getPhrase(p),doc_list,10)))
        else:
            doc_list= []
            for inter in current_user.peer_list:
                for thread in inter.thread_list:
                    doc_list.append(thread.getPhrase(p))
            for inter in current_user.peer_list:
                if(inter.email not in i_peer_list):
                    continue
                file.write(inter.email)
                for thread in inter.thread_list:
                    file.write('\n')
                    file.write('\n')
                    file.write(str(thread.subject) +'  '+str(len(thread.email_list)))
                    file.write('\n')
                    file.write(str(getTopWordsTF(thread.getPhrase(p),doc_list,10)))

    

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

