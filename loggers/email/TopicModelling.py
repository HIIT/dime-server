import os, os.path, codecs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
import numpy as np
import pickle
import lda
import textmining 
from textblob import TextBlob
os.chdir('/home/mallend1/dime-server/loggers/email') 
from classes import *

current_user = pickle.load( open( "current_user.p", "rb" ) )
li = []
for inter in current_user.peer_list:
    li.append(inter.getDocument('both'))
    
    
tdm = textmining.TermDocumentMatrix()
doc_list = [] 
p = 'both'
subject_list = []
_peer_list = []
for inter in current_user.peer_list:
    for thread in inter.thread_list:
        if not( thread.getDocument(p) == ' '):
            subject_list.append(thread.subject)
            _peer_list.append(inter.email)
            tdm.add_doc(thread.getDocument(p))
            doc_list.append(thread.getDocument(p))
    
len(doc_list)
tfidf = TfidfVectorizer(stop_words=ENGLISH_STOP_WORDS, lowercase=True, strip_accents="unicode", use_idf=True, norm="l2", min_df = 5) 
A = tfidf.fit_transform(doc_list)
num_terms = len(tfidf.vocabulary_)
terms = [""] * num_terms

for term in tfidf.vocabulary_.keys():
    terms[ tfidf.vocabulary_[term] ] = term
print "Non Negative Matrix Factorization"
print "Created document-term matrix of size %d x %d" % (A.shape[0],A.shape[1])
model = decomposition.NMF(init="nndsvd", n_components=20, max_iter=200)
W = model.fit_transform(A)
H = model.components_	
print "Generated factor W of size %s and factor H of size %s" % ( str(W.shape), str(H.shape) )
for topic_index in range( H.shape[0] ):
    top_indices = np.argsort( H[topic_index,:] )[::-1][0:10]
    term_ranking = [terms[i] for i in top_indices]
    print "Topic %d: %s" % ( topic_index, " ".join( term_ranking ) )

topics = {}
for i in range(len(subject_list)):
    topic = np.argmax(W[i, :])
    if( _peer_list[i] not in topics):
        topics[_peer_list[i]] = set([topic])
    else :
        topics[_peer_list[i]].add(topic)
print topics


vectorizer = CountVectorizer(min_df=1) 
A = vectorizer.fit_transform(doc_list)
X = A.toarray()
model = lda.LDA(n_topics=20, n_iter=500, random_state=1)
model.fit(X)
topic_word = model.topic_word_
print("type(topic_word): {}".format(type(topic_word)))
print("shape: {}".format(topic_word.shape))
n = 10
vocab = vectorizer.get_feature_names()
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n+1):-1]
    print('*Topic {} - {}'.format(i, ' '.join(topic_words)))

doc_topic = model.doc_topic_
for n in range(10):
    topic_most_pr = doc_topic[n].argmax()
    print("doc: {} topic: {} ".format(n,topic_most_pr))

topics = {}
for i in range(len(subject_list)):
    topic =  doc_topic[i].argmax()
    if( _peer_list[i] not in topics):
        topics[_peer_list[i]] = set([topic])
    else :
        topics[_peer_list[i]].add(topic)
        

print topics
