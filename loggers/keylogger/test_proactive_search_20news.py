#!/usr/bin/python

import numpy as np

import sys
import argparse

from dime_search2 import *
from update_files import *

#
import mailbox

#
import pickle

import nltk
porter = nltk.PorterStemmer()

#------------------------------------------------------------------------------

categoryindices = {
    "alt.atheism": 0,
    "comp.graphics": 1,
    "comp.os.ms-windows.misc": 2,
    "comp.sys.ibm.pc.hardware": 3,
    "comp.sys.mac.hardware": 4,
    "comp.windows.x": 5,
    "misc.forsale": 6,
    "rec.autos": 7,
    "rec.motorcycles": 8,
    "rec.sport.baseball": 9,
    "rec.sport.hockey": 10,
    "sci.crypt": 11,
    "sci.electronics": 12,
    "sci.med": 13,
    "sci.space": 14,
    "soc.religion.christian": 15,
    "talk.politics.guns": 16,
    "talk.politics.mideast": 17,
    "talk.politics.misc": 18,
    "talk.religion.misc": 19 }

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
def compute_doccategorylist_20news(jsons):

    doccategorylist = []
    for jsond in jsons:
        #print(jsond['tags'])
        dstr=''
        sublist = []
        for tag in jsond['tags']:
            parts = tag.split('=')
            if parts[0] == "newsgroup":
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
args = parser.parse_args()

#User ini
srvurl, usrname, password, time_interval, nspaces, numwords_disabled, updateinterval, data_update_interval, nokeypress_interval = read_user_ini()
#
numwords = args.numwords

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
doccategorylist = compute_doccategorylist_20news(data)

if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')

#

if not args.queries:
    print("args.queries is empty")
    sys.exit()

if not args.querypath:
    print("args.querypath is empty")
    sys.exit()

#
filelocatorlist = []

#
dwordlist = []

filecategory_old = None

#
filename = args.queries
print("Reading simulation queries from file", filename)

#
f = open(filename,'r')

for j,line in enumerate(f):

    #dstr = line.read()
    line        = line.rstrip()
    dlist       = line.split("/")
    filename    = line
    filecategory= categoryindices[dlist[1]]
    #print "filename2: ", dlist[0], dlist[1]
    #print 'enron_with_categories/'+dlist[0]
    #dumfile = open('enron_with_categories/'+dlist[0])

    #print "Message ",j
    #
    #mbox = mailbox.mbox(parts[0])
    mbox = mailbox.mbox(args.querypath+'/'+filename)
    if len(mbox) != 1:
        print("ERROR: Multiple emails (", len(mbox), ") found in", filename)
        break
    for message in mbox:
        #json_payload = create_payload(message, i, parts[1], parts[2])
        subject          = message['subject']
        #print subject
        subject = filter_string(subject, not args.nostem)
        #print subject
        subject_wordlist = subject.split()
        #print subject

        msgpayload = message.get_payload()
        #print msgpayload
        msgpayload = filter_string(msgpayload, not args.nostem)

        msgpayload_wordlist = msgpayload.split()

        wordlist = subject_wordlist + msgpayload_wordlist
        #print msgpayload_wordlist

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
            all_kw_scores = []
            for ii in range(0,20):
                kwm, foo = compute_topic_keyword_scores(sXarray, winds, doccategorylist, ii)
                all_kw_scores.append(kwm)
            kw_scores = all_kw_scores[filecategory]
            if filecategory_old is not None:
                kw_scores_old = all_kw_scores[filecategory_old]
            else:
                kw_scores_old = kw_scores

            sum_of_all_kw_scores = sum(all_kw_scores)
            kw_scores_norm = kw_scores/sum_of_all_kw_scores
            kw_scores_norm_old = kw_scores_old/sum_of_all_kw_scores

            #Number of files having same category
            nsamecategory = 0.0
            nsamecategory_old = 0.0

            #Print all tags of jsons
            for json in jsons:
                print("Tags: ", json['tags']) 
                #Split file -tag for checking category
                for ti, tag in enumerate(json['tags']):
                    parts = json['tags'][ti].split('=')
                    if parts[0] == "newsgroup":
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
            print("  ", all_kw_scores/sum_of_all_kw_scores, '\n')

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

