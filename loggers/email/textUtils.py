import math
from textblob import TextBlob as tb
import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

def preProcess(sentence):
	sentence = sentence.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	tokens = tokenizer.tokenize(sentence)
	filtered_words = [stemmer.stem(w) for w in tokens if not w in stopwords.words('english')]
	return " ".join(filtered_words)
 
def tf(word, blob):
    return float(blob.words.count(word)) / len(blob.words)
 
def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)
 
def idf(word, bloblist):
    #print word
    #print (1 + n_containing(word, bloblist))
    #print (float(len(bloblist) )/ (1 + n_containing(word, bloblist)))
    return math.log(float(len(bloblist)) / (1 + n_containing(word, bloblist)))
 

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)


def getTopWordsTFIDF(blob,bloblist,k):
    scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    topWords = []
    for word, score in sorted_words[:k]:
        new = []
        new.append(word)
        new.append(round(score, 5))
        topWords.append(new)
        #print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
    return topWords
