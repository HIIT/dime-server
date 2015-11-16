import numpy as np
import json

from dime_search2 import  *
#from json import *
import math

import random

#
#Some additional functions that are used in various places, e.g. in functions of dime_search.py
#

#For computing sparsity of a vector
def vec_sparsity(v):
    
    #
    nrows = 0
    ncols = 0

    #
    try:
        nrows, ncols = v.shape
    except ValueError:
        nrows = v.shape[0]

    #
    if nrows > ncols:
        n = nrows
        sqrt_n = math.sqrt(n)
        l1 = float(np.linalg.norm(v,1))
    else:

        n = ncols
        #print(n)
        sqrt_n = math.sqrt(n)
        l1 = float(np.linalg.norm(v.T,1))

    #L_1-norm
    #l1 = np.linalg.norm(v,1)
    #l1 = float(l1)

    #Euclidean norm, L_2-norm
    l2 = float(np.linalg.norm(v,2))

    #Sparsity
    if (sqrt_n - 1) > 0 and l2 > 0 :
        spar = (sqrt_n - (l1/l2))/(sqrt_n - 1)
    else:
        return 0.0

    return spar

#Compute cosine similarity between two vectors
def cossim(x1,x2):
	pass

#
def check_history_removal_vsum(frac_thres, mvn_avg_n):

    frac = 0.0

    if os.path.isfile("data/cossim_vsum_vec.npy"):
        cossim_vsum_vec = np.load('data/cossim_vsum_vec.npy')
    else:
        cossim_vsum_vec = [0]        

    #Take latest value of cosine similarity between consecutive vsum-vectors
    latest_cossim = cossim_vsum_vec[-1:]
    #Compute moving average
    #mvng_avg      = cossim_vsum_vec[-11:-1].mean()
    mvng_avg      = cossim_vsum_vec[-(mvn_avg_n+1):-1].mean()
    if (1-mvng_avg) > 0.0:
        frac      = (1-latest_cossim)/(1-mvng_avg)
        if frac > frac_thres:
            print("REMOVING HISTORY!")
            if os.path.isfile('data/r_old.npy'):
                os.remove('data/r_old.npy')

    return frac


def check_history_removal_w_hat(frac_thres, mvn_avg_n):

    frac = 0.0

    if os.path.isfile("data/eucl_dist_w_hat_vec.npy"):
        eucl_dist_w_hat_vec = np.load('data/eucl_dist_w_hat_vec.npy')
    else:
        eucl_dist_w_hat_vec = [0]        

    #Take latest value of cosine similarity between consecutive w_hat-vectors
    latest_eucl_dist = eucl_dist_w_hat_vec[-1:]
    #Compute moving average
    mvng_avg      = eucl_dist_w_hat_vec[-(mvn_avg_n+1):-1].mean()
    if mvng_avg > 0.0:
        frac      = latest_eucl_dist/mvng_avg
        if frac > frac_thres:
            print("REMOVING HISTORY!")
            if os.path.isfile('data/r_old.npy'):
                os.remove('data/r_old.npy')

    return frac


def check_history_removal_norm_sigma_hat(frac_thres, mvn_avg_n):

    frac = 0.0

    if os.path.isfile("data/norm_sigma_hat.npy"):
        eucl_dist_w_hat_vec = np.load('data/norm_sigma_hat.npy')
    else:
        eucl_dist_w_hat_vec = [0]

    #Take latest value of cosine similarity between consecutive w_hat-vectors
    latest_eucl_dist = eucl_dist_w_hat_vec[-1:]
    #Compute moving average
    mvng_avg      = eucl_dist_w_hat_vec[-(mvn_avg_n+1):-1].mean()
    if mvng_avg > 0.0:
        frac      = latest_eucl_dist/mvng_avg
        if frac > frac_thres:
            print("REMOVING HISTORY!")
            if os.path.isfile('data/r_old.npy'):
                os.remove('data/r_old.npy')

    return frac



#Compute list of topic ids corresponding each document id
def compute_doccategorylist_enron():
    #
    #print('hello')
    f = open('data/json_data.txt','r')
    jsons = json.load(f)

    doccategorylist = []
    for jsond in jsons:
        #print(jsond['tags'])
        dstr=''
        sublist = []
        for tag in jsond['tags']:
            if tag.split('=')[0] == 'enron_category':
                category = int(tag.split('=')[1].split(':')[0])
                sublist.append(category)
                #dstr = dstr + ' ' + str(category)    
        doccategorylist.append(sublist)

    #print(doccategorylist)
    pickle.dump(doccategorylist,open('data/doccategorylist.list','wb'))
    print(len(doccategorylist))
    return doccategorylist
    #return 0
    #pass

#Compute topic scores of each keywords given the writing topic 'writin_topic'
def compute_topic_keyword_scores(tfidf_matrix, keywordindlist, doccategorylist, writing_topic):

    #input:
    #tfidf_matrix
    #doccategorylist = list of topic ids corresponding each document id
    #
    #output:
    #kw_scores.mean() = mean of mean values of tfidf values of suggested keywords with respect to the writing topic
    #kw_scores        = list of mean values of suggested keywords with respect to the writing topic

    if len(keywordindlist)==0:
        return 0, []

    #
    sub_tfidf_matrix = tfidf_matrix[:,keywordindlist]
    #print(sub_tfidf_matrix.shape)

    #Initialize boolean numpy vector 
    boolvec = np.zeros((len(doccategorylist),), dtype=bool)
    for i,doctopics in enumerate(doccategorylist):
        #print(i,doctopics,writing_topic)
        if writing_topic in doctopics:
            boolvec[i] = True
        
    #
    if np.max(boolvec) == False:
        return 0, []

    #
    sub_tfidf_matrix = sub_tfidf_matrix[boolvec, :]

    #
    kw_scores = sub_tfidf_matrix.mean(0)

    #
    return kw_scores.mean(), kw_scores


#Pick random keyword using categorical random distribution
def pick_random_kw_ind(kw_scores_filecategory):
    
    #
    sum_kw_scores_filecategory = kw_scores_filecategory.sum()
    #print("pick_random_kw_ind: ", sum_kw_scores_filecategory)

    #Take random value from range [0,1] 
    rv = random.random()
    #
    rv = rv*sum_kw_scores_filecategory

    #print("pick_random_kw_ind: ", rv)
    #
    dv = 0
    for i,v in enumerate(kw_scores_filecategory):
        dv = dv + kw_scores_filecategory[i]
        if not rv > dv:
            #print(i)
            return i

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
def twotuplelist2fulllist(tuplelist, nfeatures):
    #
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





if __name__ == "__main__":

    #    
    doccategorylist = compute_doccategorylist()

    #Load tfidf_matrix
    sX = load_sparse_csc('data/sX.sparsemat.npz')
    sX = sX.toarray()
    print(type(sX), sX.shape)

    #
    kw_scores = compute_topic_keyword_scores(sX, [400,600], doccategorylist, 3)
    print(kw_scores)

  # v = np.random.randint(0,3,[5,1])
  # s = vec_sparsity(v)
  # print(v)
  # print(s)
