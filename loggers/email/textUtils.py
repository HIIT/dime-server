import math
from textblob import TextBlob as tb
import string
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import re
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
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
    

def preProcess(sentence):
    sentence = sentence.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    sentence = re.sub(pattern, ' ', sentence)
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
