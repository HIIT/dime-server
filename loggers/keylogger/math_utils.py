import numpy as np
import json

from dime_search2 import  *
#from json import *


#For computing sparsity of a vector
def vec_sparsity(v):
    #
    nrows, ncols = v.shape
    if nrows > ncols:
        n = nrows
        sqrt_n = np.sqrt(n)
    else:
        n = ncols
        sqrt_n = np.sqrt(n)

    #L_1-norm
    l1 = np.linalg.norm(v,1)
    l1 = float(l1)

    #Euclidean norm, L_2-norm
    l2 = np.linalg.norm(v,2)

    #Sparsity
    if n > 0 and l1 > 0 :
        spar = (sqrt_n - (l1/l2))/(sqrt_n - 1)
    else:
        return 0.0

    return spar

#Compute cosine similarity between two vectors
def cossim(x1,x2):
	pass


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
    #
    # if len(keywordindlist)==0:
    #     return 0, [0]
    sub_tfidf_matrix = tfidf_matrix[:,keywordindlist]
    #print(sub_tfidf_matrix.shape)
    #
    #boolvec = docid_topicid_list == writing_topic
    #doccategorylist = compute_doccategorylist()
    #Initialize boolean numpy vector 
    boolvec = np.zeros((len(doccategorylist),), dtype=bool)
    for i,doctopics in enumerate(doccategorylist):
        if writing_topic in doctopics:
            boolvec[i] = True
    
    sub_tfidf_matrix = sub_tfidf_matrix[boolvec, :]
    #print(sub_tfidf_matrix.shape)

    #kw_scores = sub_tfidf_matrix.sum(0)
    kw_scores = sub_tfidf_matrix.mean(0)

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
