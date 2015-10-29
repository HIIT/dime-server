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

#
import random

import nltk
porter = nltk.PorterStemmer()

#------------------------------------------------------------------------------

categoryindices_20news = {
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
gt_tag_20news = "newsgroup"
usrname_20news = password_20news = "20news-nostem"

categoryindices_reuters = {
    "acq": 0,
    "crude": 1,
    "earn": 2,
    "grain": 3,
    "interest": 4,
    "money-fx": 5,
    "ship": 6,
    "trade": 7 }
gt_tag_reuters = "category"
usrname_reuters = password_reuters = "reuters-r8-all"

categoryindices_ohsumed = {
    "C01": 0,
    "C02": 1,
    "C03": 2,
    "C04": 3,
    "C05": 4,
    "C06": 5,
    "C07": 6,
    "C08": 7,
    "C09": 8,
    "C10": 9,
    "C11": 10,
    "C12": 11,
    "C13": 12,
    "C14": 13,
    "C15": 14,
    "C16": 15,
    "C17": 16,
    "C18": 17,
    "C19": 18,
    "C20": 19,
    "C21": 20,
    "C22": 21,
    "C23": 22
}
gt_tag_ohsumed = "category"
usrname_ohsumed = password_ohsumed = "ohsumed"

#------------------------------------------------------------------------------

def process_input_file_20news(line, j, qfn):

    dlist       = line.split("/")
    filename    = line
    filecategory= categoryindices[dlist[1]]

    mbox = mailbox.mbox(args.querypath+'/'+filename)
    if len(mbox) != 1:
        print("ERROR: Multiple emails (", len(mbox), ") found in", filename)
        return None, None, None
    for message in mbox:
        subject          = message['subject']
        subject = filter_string(subject, not args.nostem)
        subject_wordlist = subject.split()

        msgpayload = message.get_payload()
        msgpayload = filter_string(msgpayload, not args.nostem)
        msgpayload_wordlist = msgpayload.split()

        wordlist = subject_wordlist + msgpayload_wordlist        

    return filename, filecategory, wordlist

#------------------------------------------------------------------------------

def process_input_file_reuters(line, j, qfn):
    parts = line.split("\t")
    filename = qfn+'_'+str(j)
    filecategory= categoryindices[parts[0]]
    wordlist = parts[1].split(" ")

    return filename, filecategory, wordlist

#------------------------------------------------------------------------------

def process_input_file_ohsumed(line, j, qfn):

    dlist       = line.split("/")
    filename    = line
    filecategory= categoryindices[dlist[0]]

    with open (args.querypath+'/'+filename, "r") as myfile:
        abstext = myfile.read()
    wordlist = abstext.split()

    return filename, filecategory, wordlist

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
def compute_doccategorylist(jsons):

    doccategorylist = []
    for jsond in jsons:
        #print(jsond['tags'])
        dstr=''
        sublist = []
        for tag in jsond['tags']:
            parts = tag.split('=')
            if parts[0] == gt_tag:
                category = categoryindices[parts[1]]
                sublist.append(category)
                #dstr = dstr + ' ' + str(category)
        doccategorylist.append(sublist)

    #print(doccategorylist)
    print("Doccategorylist size:", len(doccategorylist))
    return doccategorylist

#------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("dataset", metavar = "DATASET", 
                    help="used dataset: 20news,reuters,ohsumed")
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
parser.add_argument('--nwritten', metavar='N', action='store', type=int,
                    default=50, help='number of words to write')
parser.add_argument('--nclicked', metavar='X[:Y]',
                    help='click X suggested keywords with method Y')
parser.add_argument('--randomstart', action='store_true',
                    help='start from a random position instead of beginning')
parser.add_argument('--writeold', metavar='X:Y',
                    help='write X words from old document at position Y')

args = parser.parse_args()

#User ini
srvurl, usrname_disabled, password_disabled, time_interval, nspaces, numwords_disabled, updateinterval, data_update_interval, nokeypress_interval, mu, n_results = read_user_ini()
#
numwords = args.numwords

if args.dataset == "20news":
    categoryindices = categoryindices_20news
    gt_tag = gt_tag_20news
    process_input_file = process_input_file_20news
    usrname = usrname_20news
    password = password_20news
elif args.dataset == "reuters":
    categoryindices = categoryindices_reuters
    gt_tag = gt_tag_reuters
    process_input_file = process_input_file_reuters
    usrname = usrname_reuters
    password = password_reuters
elif args.dataset == "ohsumed":
    categoryindices = categoryindices_ohsumed
    gt_tag = gt_tag_ohsumed
    process_input_file = process_input_file_ohsumed
    usrname = usrname_ohsumed
    password = password_ohsumed
else:
    print("Unsupported dataset:", args.dataset)
    sys.exit()
    
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

nclicked_n = 0
nclicked_method = 0
if args.nclicked:
    print(args.nclicked)
    parts = args.nclicked.split(":")
    nclicked_n = int(parts[0])
    if len(parts)>1:
        nclicked_method = int(parts[1])

writeold_n = 0
writeold_pos = 0
if args.writeold:
    print(args.writeold)
    parts = args.writeold.split(":")
    writeold_n = int(parts[0])
    if len(parts)>1:
        writeold_pos = int(parts[1])

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
doccategorylist = compute_doccategorylist(data)

if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')

#


#
filelocatorlist = []

#
dwordlist = []

filecategory_old = None

wordlist_old = []

#
print("Reading simulation queries from file", args.queries)

#
f = open(args.queries, 'r')

qparts = args.queries.rsplit("/",1)
qfn = qparts[1]

for j,line in enumerate(f):

    line        = line.rstrip()
    
    filename, filecategory, wordlist = process_input_file(line, j, qfn)
    if filename is None:
        break

    if args.randomstart:
        random.seed(j)
        newfirst = random.randrange(len(wordlist))
        wordlist = wordlist[newfirst:] + wordlist[:newfirst]

    wordlist_r = list(reversed(wordlist[:writeold_pos]+wordlist_old[:writeold_n]+wordlist[writeold_pos:]))
    #print(wordlist)
    #print(wordlist_old)
    #print(wordlist_r)

    wordlist_old = wordlist.copy()

    # #Exploration/Exploitation coefficient
    c = 1.0

    #Remove r_old.npy = old version of observed relevance vector
    if not args.norestart:    
        if os.path.isfile('data/r_old.npy'):
            os.remove('data/r_old.npy')
        dwordlist = []

    #
    i2= 0
    #Number of currently typed words
    divn = 1
    #
    dstr2 = ''
    #Go through words of wordlist of a single message
    #dummy index
    j2 = 0

    #Maximum number of words written from each file 
    #Average precision
    sumavgprecision = 0.0
    sumavgprecision_old = 0.0
    #List of precisionlist corresponding one file
    precisionlist = []
    precisionlist_old = []

    kws = []

    i = 0
    while len(wordlist_r)>0:                
        dstr = wordlist_r.pop()

        #If nth word has been written, do search
        if i%divn == 0:

            #
            j2 = j2 + 1

            #
            if i2 == 0:
                print("###########################################")
                print("STARTING NEW ARTICLE no. ", j)
                print("###########################################")
                filelocatorlist.append(1.0)
            else:
                filelocatorlist.append(0.0)

            print("Filename:", filename, "j:", j, "i:", i, "dstr:", dstr)
            dwordlist.append(dstr)
            dstr2 = dstr2 + ' ' + dstr
            #print "Currently typed: ", dstr2
            dstr2 = dwordlist[-numwords:]
            dstr2 = ' '.join(dstr2)
            print("Input to search function: ", dstr2)
            jsons, kws, winds = search_dime_linrel_keyword_search_dime_search(dstr2, sX, tfidf, dictionary, c, mu, srvurl, usrname, password, n_results)
            nsuggested_files = len(jsons)

            #
            if args.removeseenkws:
                test_wordlist = pickle.load(open('data/test_wordlist.list','rb'))
                print("TEST_WORDLIST:", test_wordlist)
                new_kws = []
                new_winds = []
                for iii,kw in enumerate(kws):
                    if kw not in test_wordlist:
                        new_kws.append(kws[iii])
                        new_winds.append(winds[iii])
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
            for ii in range(0,len(categoryindices)):
                kwm, kw_scores_topic = compute_topic_keyword_scores(sXarray, winds, doccategorylist, ii)
                if ii == filecategory:
                    if len(kw_scores_topic) > 0:
                        #print(len(kw_scores_topic))
                        #print(type(kw_scores_topic))
                        kw_scores_filecategory = kw_scores_topic
                        kw_scores_filecategory = np.array(kw_scores_filecategory)
                        #print(kw_scores_filecategory)
                        kw_maxind = np.argmax(kw_scores_filecategory)
                        #
                        kw_randind = pick_random_kw_ind(kw_scores_filecategory) 
                        #print("kw_maxind: ", kw_maxind)
                    else:
                        kw_maxind = 0
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
                    if parts[0] == gt_tag:
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
            print("  ", all_kw_scores_norm)

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

        i = i+1
        if i>=(args.nwritten+nclicked_n):
            break
        elif i>=(args.nwritten):
            try:
                if nclicked_method == 3:
                    if len(kws)>0:
                        kw_randind2 = random.randint(0,len(kws)-1)
                        kw_clicked  = kws[kw_randind2]
                    else:
                        kw_clicked = kws[0]
                elif nclicked_method == 2:
                    if kw_randind>len(kws)-1:
                        kw_randind = kw_maxind
                    kw_clicked = kws[kw_randind]
                elif nclicked_method == 1:
                    kw_clicked = kws[kw_maxind]
                else:
                    kw_clicked = kws[0]
                print("Adding clicked keyword", kw_clicked, "using method", nclicked_method)
                wordlist_r.append(kw_clicked)
            except IndexError:
                print("Adding clicked keyword failed, breaking out")
                break

        print()

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

