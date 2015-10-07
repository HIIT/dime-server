import numpy as np
import json

from dime_search2 import  *
#from json import *
import math

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

#Compute topic scores of each keywords 
def compute_topic_keyword_scores(tfidf_matrix, keywordindlist, doccategorylist, writing_topic):
    #input:
    #tfidf_matrix
    #doccategorylist = list of topic ids corresponding each document id
    #
    #output:
    #kw_scores.mean() = list of topic related mean of tfidf values of suggested keywords

    if len(keywordindlist)==0:
        return 0, []

    sub_tfidf_matrix = tfidf_matrix[:,keywordindlist]
    #print(sub_tfidf_matrix.shape)
    #
    #boolvec = docid_topicid_list == writing_topic
    #doccategorylist = compute_doccategorylist()
    #Initialize boolean numpy vector 
    boolvec = np.zeros((len(doccategorylist),), dtype=bool)
    for i,doctopics in enumerate(doccategorylist):
        #print(i,doctopics,writing_topic)
        if writing_topic in doctopics:
            boolvec[i] = True
        
    #print("MAX", np.max(boolvec))
    if np.max(boolvec) == False:
        return 0, []
    #
    sub_tfidf_matrix = sub_tfidf_matrix[boolvec, :]

    #
    kw_scores = sub_tfidf_matrix.mean(0)

    #Compute scores of keywords for writing_topic


    return kw_scores.mean(), kw_scores


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
