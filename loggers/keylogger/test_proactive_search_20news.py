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

parser = argparse.ArgumentParser()
parser.add_argument("--queries", metavar = "FILE", 
                    help="list of queries to process")
parser.add_argument("--querypath", metavar = "PATH", 
                    help="path to queries to process")
parser.add_argument('--nostem', action='store_true',
                    help='disable Porter stemming of tokens')
args = parser.parse_args()

#User ini
srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval, data_update_interval, nokeypress_interval = read_user_ini()
#
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
index      = similarities.docsim.Similarity.load('/tmp/similarityvec')

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
    filecategory= dlist[1]
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
    if os.path.isfile('data/r_old.npy'):
        os.remove('data/r_old.npy')

    #
    i = 0
    i2= 0
    #Number of currently typed words
    divn = 1
    #
    dstr2 = ''
    dwordlist = []
    #Go through words of wordlist of a single message
    #dummy index
    j2 = 0

    #Maximum number of words written from each file 
    nwritten = 50
    #Average precision
    sumavgprecision = 0.0
    #List of precisionlist corresponding one file
    precisionlist = []
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
            jsons, kws = search_dime_linrel_keyword_search_dime_search(dstr2, sX, tfidf, dictionary, c, srvurl, usrname, password)                
            nsuggested_files = len(jsons)


            #Number of files having same category
            nsamecategory = 0.0

            #Print all tags of jsons
            for json in jsons:
                print("Tags: ", json['tags']) 
                #Split file -tag for checking category
                for ti, tag in enumerate(json['tags']):
                    parts = json['tags'][ti].split('=')
                    if parts[0] == "newsgroup":
                        #
                        categoryid = parts[1]
                        print("Category:", categoryid, "Correct:", filecategory)
                        #
                        if categoryid == filecategory:
                            print("GOT SAME CATEGORY!")
                            nsamecategory = nsamecategory + 1.0
                            #break

            #Current precision
            if nsuggested_files > 0:
                cprecision = float(nsamecategory)/float(nsuggested_files)
            else:
                cprecision = 0

            #Average precision so far
            sumavgprecision = sumavgprecision + cprecision
            if j2 > 0:
                avgprecision = float(sumavgprecision)/float(j2)
            else:
                avgprecision = 0
            #
            print("Precisions: ",cprecision, avgprecision)
            #
            precisionlist.append([cprecision, avgprecision])

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
    f = open('data/precisionlist_'+filename+'.list','w')
    pickle.dump(precisionlist,f)


