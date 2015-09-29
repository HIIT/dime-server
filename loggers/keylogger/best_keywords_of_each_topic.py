from math_utils import *

#
import pickle

#
import matplotlib.pyplot as plt
#from matplotlib import imshow

#Load updated tfidf-matrix of the corpus
sX         = load_sparse_csc('data/sX.sparsemat.npz')
sXarray    = sX.toarray()

#Load dictionary
dictionary = corpora.Dictionary.load('data/tmpdict.dict')
wkeys = [i for i in range(len(dictionary))]
#print(wkeys)
#print(len(dictionary.keys()))
#Compute topics of each document
doccategorylist = compute_doccategorylist()
doccategorylist = pickle.load(open('data/doccategorylist.list','rb'))

#
all_kw_scores = []
topic_words = []
for i in range(1,13):   
    #print(dictionary.keys()[0])
    #kw_mean, kw_scores = compute_topic_keyword_scores(sXarray, dictionary.keys(), doccategorylist, i)
    kw_mean, kw_scores = compute_topic_keyword_scores(sXarray, wkeys, doccategorylist, i)
    all_kw_scores.append(kw_scores) 

    #Take take indices of elements of kw_scores 'all' according to ascending order
    inds = np.argsort(kw_scores[:])
    inds = inds[-20:]
    inds = inds.tolist()

    #Make reversed list of vsinds
    inds.reverse()

    #Print words having largest mean tfidf value over documents belonging to some topic
    dwords = []
    for ind in inds:
        dwords.append(dictionary.get(ind))
    print(dwords,kw_mean)
    topic_words.append(dwords)
    #print(all_kw_scores[i-1].shape)


#
score_matrix_per_topic = np.array(all_kw_scores)

#
np.save('data/score_matrix_per_topic.npy',score_matrix_per_topic)
pickle.dump(all_kw_scores,open('data/kw_scores_per_topic.list','wb'))

#


#Compute how similar different topics are by computing cosine similarity 
topic_cossim = []
for row in all_kw_scores:
    dcossim = []
    for drow in all_kw_scores:
        dcossim.append( row.dot(drow)/(np.linalg.norm(row)*np.linalg.norm(drow)) )
    print(dcossim)
    topic_cossim.append(dcossim)
cosmat = np.array(topic_cossim)
#fig = plt.figure()
# plt.imshow(cosmat, interpolation='nearest', cmap=plt.cm.binary)
# plt.colorbar()
# plt.show()


# sentence1 = "dog is the"
# sentence2 = "the dog is a very nice animal"
# sentence3 = "the dog is running in your garden"
# set_sentence1 = set(sentence1.split())
# set_sentence2 = set(sentence2.split())
# set_sentence3 = set(sentence3.split())

# intersection1 = set_sentence1.intersection(set_sentence3)
# intersection2 = set_sentence2.intersection(set_sentence3)

# Similarity1 = (1.0 + len(intersection1))/(1.0 + max(len(set_sentence1), len(set_sentence3)))
# Similarity2 = (1.0 + len(intersection2))/(1.0 + max(len(set_sentence2), len(set_sentence3)))
# print(Similarity1,Similarity2)

topic_cossim2 = []
for dwords in topic_words:
    dset = set(dwords)
    dcossim2 = []
    for dwords2 in topic_words:
        dset2 = set(dwords2)
        dintersection = dset.intersection(dset2)
        dcossim2.append( (1.0 + len(dintersection))/(1.0 + max(len(dset), len(dset2))) )
    print(dcossim2)
    topic_cossim2.append(dcossim2)

cosmat2 = np.array(topic_cossim2)
#fig = plt.figure()
#plt.imshow(cosmat, interpolation='nearest', cmap=plt.cm.ocean)
plt.imshow(cosmat2, interpolation='nearest', cmap=plt.cm.binary)
plt.colorbar()
plt.show()