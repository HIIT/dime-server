#!/usr/bin/python

import numpy as np

import sys
import argparse

from dime_search2 import *
from update_files import *

#
#import mailbox

#
import pickle

import nltk
porter = nltk.PorterStemmer()

#------------------------------------------------------------------------------

categoryindices = {
    "acq": 0,
    "crude": 1,
    "earn": 2,
    "grain": 3,
    "interest": 4,
    "money-fx": 5,
    "ship": 6,
    "trade": 7 }

#------------------------------------------------------------------------------

def filter_string(string, do_stem=True):

    #tokens = nltk.word_tokenize(string)

    pattern = r'''(?x)  # set flag to allow verbose regexps
    ([A-Z]\.)+          # abbreviations, e.g. U.S.A.
    | \w+(-\w+)*        # words with optional internal hyphens
    | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
    | \.\.\.            # ellipsis
    | [][.,;"'?():-_`]  # these are separate tokens
    '''
    tokens = nltk.regexp_tokenize(string, pattern)

    tokens = [t.lower() for t in tokens]
    if do_stem:
        tokens = [porter.stem(t) for t in tokens]
    #tokens = [wnl.lemmatize(t) for t in tokens]
    return " ".join(item for item in tokens if len(item)>1)

#------------------------------------------------------------------------------

#Compute list of topic ids corresponding each document id
def compute_doccategorylist_reuters(jsons):

    doccategorylist = []
    for jsond in jsons:
        #print(jsond['tags'])
        dstr=''
        sublist = []
        for tag in jsond['tags']:
            parts = tag.split('=')
            if parts[0] == "category":
                category = categoryindices[parts[1]]
                sublist.append(category)
                #dstr = dstr + ' ' + str(category)
        doccategorylist.append(sublist)

    #print(doccategorylist)
    print("Doccategorylist size:", len(doccategorylist))
    return doccategorylist

#------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--queries", metavar = "FILE", 
                    help="list of queries to process")
parser.add_argument("--querypath", metavar = "PATH", 
                    help="path to queries to process")
parser.add_argument('--nostem', action='store_true',
                    help='disable Porter stemming of tokens')
parser.add_argument('--norestart', action='store_true',
                    help='do not restart between documents')
parser.add_argument('--numwords', metavar='N', action='store', type=int,
                    default=10, help='number of written words to consider')
parser.add_argument('--histremoval', metavar='X:Y', 
                    help='remove history with parameters X and Y')
parser.add_argument('--removeseenkws', action='store_true',
                    help='remove keywords that appear in input')

args = parser.parse_args()

#User ini
srvurl, usrname, password, time_interval, nspaces, numwords_disabled, updateinterval, data_update_interval, nokeypress_interval = read_user_ini()
#
numwords = args.numwords

if not args.queries:
    print("args.queries is empty")
    sys.exit()

if not args.querypath:
    print("args.querypath is empty")
    sys.exit()

histremoval_threshold = 0
histremoval_ma_value  = 0
if args.histremoval:
    print(args.histremoval)
    parts = args.histremoval.split(":")
    histremoval_threshold = int(parts[0])
    histremoval_ma_value  = int(parts[1])

#update_data(srvurl, usrname, password)
check_update()
#Load necessary data files 
json_data = open('data/json_data.txt')
#DiMe data in json -format
data       = json.load(json_data)
#Load df-matrix (document frequency matrix)
sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')
#Load dictionary
dictionary = corpora.Dictionary.load('data/tmpdict.dict')
#Remove common words from dictionary
#df_word_removal(sXdoctm, dictionary)
#dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
#Load updated tfidf-matrix of the corpus
sX         = load_sparse_csc('data/sX.sparsemat.npz')
sXarray    = sX.toarray()
#Load updated df-matrix
sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')      
#Load tfidf -model
tfidf      = models.TfidfModel.load('data/tfidfmodel.model')
#Load cosine similarity model for computing cosine similarity between keyboard input with documents
index      = similarities.docsim.Similarity.load('data/similarityvec')

#Compute topics of each document
doccategorylist = compute_doccategorylist_reuters(data)

if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')

#


#
filelocatorlist = []

#
dwordlist = []

filecategory_old = None

#
print("Reading simulation queries from file", args.queries)

#
f = open(args.queries,'r')

qparts = args.queries.rsplit("/",1)
qfn = qparts[1]

for j,line in enumerate(f):

    #dstr = line.read()
    line        = line.rstrip()
    parts = line.split("\t")

    filename    = qfn+'_'+str(j)
    filecategory= categoryindices[parts[0]]

    wordlist = parts[1].split(" ")

    # #Exploration/Exploitation coefficient
    c = 1.0

    #Remove r_old.npy = old version of observed relevance vector
    if not args.norestart:    
        if os.path.isfile('data/r_old.npy'):
            os.remove('data/r_old.npy')
        dwordlist = []

    #
    i = 0
    i2= 0
    #Number of currently typed words
    divn = 1
    #
    dstr2 = ''
    #Go through words of wordlist of a single message
    #dummy index
    j2 = 0

    #Maximum number of words written from each file 
    nwritten = 50
    #Average precision
    sumavgprecision = 0.0
    sumavgprecision_old = 0.0
    #List of precisionlist corresponding one file
    precisionlist = []
    precisionlist_old = []

    for i, dstr in enumerate(wordlist):

        #If nth word has been written, do search
        if i%divn == 0:

            #
            j2 = j2 + 1

            #
            if i2 == 0:
                print("\nMail ", j)
                filelocatorlist.append(1.0)
            else:
                filelocatorlist.append(0.0)
            dwordlist.append(dstr)
            dstr2 = dstr2 + ' ' + dstr
            #print "Currently typed: ", dstr2
            dstr2 = dwordlist[-numwords:]
            dstr2 = ' '.join(dstr2)
            print("Filename:", filename)
            print("Input to search function: ", dstr2)
            jsons, kws, winds = search_dime_linrel_keyword_search_dime_search(dstr2, sX, tfidf, dictionary, c, srvurl, usrname, password)
            nsuggested_files = len(jsons)

            #
            if args.removeseenkws:
                test_wordlist = pickle.load(open('data/test_wordlist.list','rb'))
                print("TEST_WORDLIST:", test_wordlist)
                new_kws = []
                new_winds = []
                for iiiii,kw in enumerate(kws):
                    if kw not in test_wordlist:
                        new_kws.append(kws[iiiii])
                        new_winds.append(winds[iiiii])
                    else:
                        print("KEYWORD", kw, "ALREADY IN INPUT, REMOVE!!")
                kws = new_kws
                winds = new_winds
                print("KWS AFTER REMOVAL:", kws)

            #
            if args.histremoval:                
                histremoval_val = check_history_removal(histremoval_threshold, histremoval_ma_value)
                if histremoval_val > histremoval_threshold:
                    dwordlist = dwordlist[-3:]

            #
            all_kw_scores = []
            for ii in range(0,8):
                kwm, foo = compute_topic_keyword_scores(sXarray, winds, doccategorylist, ii)
                all_kw_scores.append(kwm)
            kw_scores = all_kw_scores[filecategory]
            if filecategory_old is not None:
                kw_scores_old = all_kw_scores[filecategory_old]
            else:
                kw_scores_old = kw_scores

            sum_of_all_kw_scores = max(sum(all_kw_scores),0.0000000001)
            kw_scores_norm = kw_scores/sum_of_all_kw_scores
            kw_scores_norm_old = kw_scores_old/sum_of_all_kw_scores
            all_kw_scores_norm = [x / sum_of_all_kw_scores for x in all_kw_scores]

            #Number of files having same category
            nsamecategory = 0.0
            nsamecategory_old = 0.0

            #Print all tags of jsons
            for json in jsons:
                print("Tags: ", json['tags']) 
                #Split file -tag for checking category
                for ti, tag in enumerate(json['tags']):
                    parts = json['tags'][ti].split('=')
                    if parts[0] == "category":
                        #
                        categoryid = categoryindices[parts[1]]
                        print("Category:", categoryid, "Correct:", filecategory, "Old:", filecategory_old)
                        #
                        if categoryid == filecategory:
                            print("GOT SAME CATEGORY AS CURRENT!")
                            nsamecategory = nsamecategory + 1.0
                        elif categoryid == filecategory_old:
                            print("GOT SAME CATEGORY AS OLD!")
                            nsamecategory_old = nsamecategory_old + 1.0

            #Current precision
            if nsuggested_files > 0:
                cprecision = float(nsamecategory)/float(nsuggested_files)
                cprecision_old = float(nsamecategory_old)/float(nsuggested_files)
            else:
                cprecision = 0
                cprecision_old = 0

            #Average precision so far
            sumavgprecision = sumavgprecision + cprecision
            sumavgprecision_old = sumavgprecision_old + cprecision_old
            if j2 > 0:
                avgprecision = float(sumavgprecision)/float(j2)
                avgprecision_old = float(sumavgprecision_old)/float(j2)
            else:
                avgprecision = 0
                avgprecision_old = 0
            #
            print("Suggested keywords:", kws)
            print("Current: precisions: ",cprecision, avgprecision, 'kw_scores: ', kw_scores, 'normalized:', kw_scores_norm)
            print("Old:     precisions: ",cprecision_old, avgprecision_old, 'kw_scores: ', kw_scores_old, 'normalized:', kw_scores_norm_old)
            print("  ", all_kw_scores_norm, '\n')

            #
            precisionlist.append([cprecision, avgprecision, kw_scores_norm])
            precisionlist_old.append([cprecision_old, avgprecision_old, kw_scores_norm_old])

            #
            dstr2 = ''
        else:
            dwordlist.append(dstr)
            dstr2 = dstr2 + ' ' + dstr
        #
        i2 = i2 + 1

        #If number of written words from the current file is bigger than nwritten, break 
        if i>nwritten:
            break

    #
    filelocatorlistnp = np.array(filelocatorlist)
    np.save('data/filelocatorlist.npy',filelocatorlistnp)

    #Save precisionlist
    filename = filename.replace('/','_')
    filename = filename.replace('.','_')
    pickle.dump(precisionlist, open('data/precisionlist_'+filename+'.list','wb'))
    if filecategory != filecategory_old and filecategory_old is not None:
        pickle.dump(precisionlist_old, open('data/precisionlistold_'+filename+'.list','wb'))

    filecategory_old = filecategory

