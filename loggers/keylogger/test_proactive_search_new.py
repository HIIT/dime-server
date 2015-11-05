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

import xml.etree.ElementTree as ET

from dataset_definitions import *

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

def process_input_file_arxivcs(line, j, qfn):

    doc = root[int(line)]

    filename, filecategory, wordlist = None, None, []
    for field in doc:
        text = field.text
        if not 'name' in field.attrib:
            continue
        nameattr = field.attrib['name']
        if nameattr == 'id':
            filename = text
        elif nameattr == 'abstract':
            wordlist = text.split()
        elif nameattr == 'subject' and text in text2cat_arxivcs:
            filecategory = categoryindices[text2cat_arxivcs[text]]

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
                    help="used dataset: 20news,reuters,reuters52,ohsumed,arxivcs")
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
parser.add_argument("--xmlfile", metavar = "XMLFILE", 
                    help="XML file to read, needed by arxivcs")

#
parser.add_argument('--c', metavar='N', action='store', type=float,
                    default=1.0, help='Exploration/Exploitation coeff.')
parser.add_argument('--dime_search_method', metavar='N', action='store', type=int,
                    default=1, help='1: DiMe search + LinRel \n 2: Weighted DiMe search with 10 added keywords, \n 3: Weighted DiMe search using only 10 keywords')


args = parser.parse_args()

#User ini
srvurl, usrname_disabled, password_disabled, time_interval, nspaces, numwords_disabled, updateinterval, data_update_interval, nokeypress_interval, mu, n_results = read_user_ini()
#
numwords = args.numwords

if args.xmlfile:
    print("Parsing XML, this may take a while")
    tree = ET.parse(args.xmlfile)
    root = tree.getroot()
    print("Parsing XML done")

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
elif args.dataset == "reuters52":
    categoryindices = categoryindices_reuters52
    gt_tag = gt_tag_reuters
    process_input_file = process_input_file_reuters
    usrname = usrname_reuters52
    password = password_reuters52
elif args.dataset == "ohsumed":
    categoryindices = categoryindices_ohsumed
    gt_tag = gt_tag_ohsumed
    process_input_file = process_input_file_ohsumed
    usrname = usrname_ohsumed
    password = password_ohsumed
elif args.dataset == "arxivcs":
    categoryindices = categoryindices_arxivcs
    gt_tag = gt_tag_arxivcs
    process_input_file = process_input_file_arxivcs
    usrname = usrname_arxivcs
    password = password_arxivcs
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
check_update(usrname, password)
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

#If file 'r_old.npy' exist, remove it
if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')

#


#
filelocatorlist = []

#
dwordlist = []

#
filecategory_old = None

#
wordlist_old = []

#
print("Reading simulation queries from file", args.queries)

#
f = open(args.queries, 'r')

qparts = args.queries.rsplit("/",1)
qfn = qparts[1]

#Loop through documents to be written
for j,line in enumerate(f):

    line        = line.rstrip()
    
    filename, filecategory, wordlist = process_input_file(line, j, qfn)
    if filename is None:
        break
    if filecategory is None:
        continue

    if args.randomstart:
        random.seed(j)
        newfirst = random.randrange(len(wordlist))
        wordlist = wordlist[newfirst:] + wordlist[:newfirst]

    #Reverse the order of words in the documents
    wordlist_r = list(reversed(wordlist[:writeold_pos]+wordlist_old[:writeold_n]+wordlist[writeold_pos:]))
    #print(wordlist)
    #print(wordlist_old)
    #print(wordlist_r)

    wordlist_old = wordlist.copy()

    # #Exploration/Exploitation coefficient
    c = args.c

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

    #Initialize list of keywords
    kws = []

    #Number of words written from the current document
    i = 0

    #Go through words in word list corresponding the current document
    while len(wordlist_r)>0:             

        #Store the next word in document and remove it from the corresponding word list
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

            #jsons, kws, winds = search_dime_linrel_keyword_search_dime_search(dstr2, sX, tfidf, dictionary, c, mu, srvurl, usrname, password, n_results)
            #Search docs from DiMe and compute keywords
            if args.dime_search_method == 1:
                jsons, kws, winds = search_dime_linrel_keyword_search_dime_search(dstr2, sX, tfidf, dictionary, c, mu, srvurl, usrname, password, n_results)
            elif args.dime_search_method == 2:
                #Number of keywords added to query
                n_kws = 10
                jsons, kws, winds = search_dime_using_linrel_keywords(dstr2, n_kws, sX, tfidf, dictionary, c, mu, srvurl, usrname, password, n_results)
            elif args.dime_search_method == 3:
                #Number of keywords added to query
                n_kws = 10
                jsons, kws, winds = search_dime_using_only_linrel_keywords(dstr2, n_kws, sX, tfidf, dictionary, c, mu, srvurl, usrname, password, n_results)
            

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
                    
            #Number of keywords appearing in GUI
            n_kws = 10
            kws = kws[0:n_kws]
            #
            winds = winds[0:n_kws]
            #Compute keyword scores here for the n_kws keywords
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

        #
        i = i + 1

        #If number of written and clicked words is bigger than args.nwritten + arg.nclicked, 
        #stop while-loop of current document 
        if i>=(args.nwritten+nclicked_n):
            break
        #If number of words written from the current document is greater than
        #args.nwritten click the suggested keyword using some clicking model
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

    #Save list of locators of documents that are written
    filelocatorlistnp = np.array(filelocatorlist)
    np.save('data/filelocatorlist.npy',filelocatorlistnp)

    #Save precisionlist corresponding the written document
    filename = filename.replace('/','_')
    filename = filename.replace('.','_')
    filename = filename.replace(':','_')
    pickle.dump(precisionlist, open('data/precisionlist_'+filename+'.list','wb'))
    if filecategory != filecategory_old and filecategory_old is not None:
        pickle.dump(precisionlist_old, open('data/precisionlistold_'+filename+'.list','wb'))

    #Store the old filecategory for precision value comparison
    filecategory_old = filecategory

