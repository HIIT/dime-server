import numpy as np

import argparse

from dime_search2 import *
from update_files import *

#
from math_utils import *

#
import mailbox

#
import nltk
porter = nltk.PorterStemmer()

import pickle
#compute_topic_keyword_scores


def filter_string(string):

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
    tokens = [porter.stem(t) for t in tokens]
    #tokens = [wnl.lemmatize(t) for t in tokens]
    return " ".join(item for item in tokens if len(item)>1)
    return " ".join(item for item in tokens if len(item)>1)

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
#Load updated df-matrix of the corpus
sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')      
#Load tfidf -model
tfidf      = models.TfidfModel.load('data/tfidfmodel.model')
#Load cosine similarity model for computing cosine similarity between keyboard input with documents
index      = similarities.docsim.Similarity.load('data/similarityvec')

#Compute topics of each document
doccategorylist = compute_doccategorylist_enron()
#print(doccategorylist)

if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')

#
parser = argparse.ArgumentParser()
#parser.add_argument("square", help="Square of the given number", type = int)
parser.add_argument("--simulation", help="increase output verbosity", metavar = "FILE")
args = parser.parse_args()

#print args.square**2
if args.simulation:
    
    #
    filelocatorlist = []

    #
    dwordlist = []

    #
    filename = args.simulation
    print("Simulation with file", filename)

    #
    f = open(filename,'r')


    for j,line in enumerate(f):
        
        #dstr = line.read()
        dlist       = line.split(" ")
        filename    = dlist[0]
        filecategory= int(dlist[1])
        print("filename2: ", dlist[0], dlist[1])
        #print 'enron_with_categories/'+dlist[0]
        #dumfile = open('enron_with_categories/'+dlist[0])

        #print "Message ",j
        #
        #mbox = mailbox.mbox(parts[0])
        mbox = mailbox.mbox('enron_with_categories/'+filename)
        if len(mbox) != 1:
            print("ERROR: Multiple emails found in", parts[0])
            break
        for message in mbox:
            #json_payload = create_payload(message, i, parts[1], parts[2])
            subject          = message['subject']
            #print subject
            subject = filter_string(subject)
            #print subject
            subject_wordlist = subject.split()
            #print subject

            msgpayload = message.get_payload()
            #print msgpayload
            msgpayload = filter_string(msgpayload)

            msgpayload_wordlist = msgpayload.split()

            wordlist = subject_wordlist + msgpayload_wordlist
            #print msgpayload_wordlist


        #Exploration/Exploitation coefficient
        c = 1.0


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
                print("Input to search function: ", dstr2)
                jsons, kws, winds = search_dime_linrel_keyword_search_dime_search(dstr2, sX, tfidf, dictionary, c, srvurl, usrname, password) 

                #Remove r_old.npy = old version of observed relevance vector
                #Load cossim_vsum_vec for computing moving average with 10 previous cosine similarity values
                
                #Maximum fraction threshold
                frac_thres = 5.0
                #Number of past values from which the average is computed
                mvn_avg_n  = 10
                #frac = 0.0
                frac = check_history_removal(frac_thres, mvn_avg_n)
                if frac > frac_thres:
                    dwordlist = []

                # 
                all_kw_scores = []
                for i in range(1,13):
                    kw_scores_mean, kw_scores = compute_topic_keyword_scores(sXarray, winds, doccategorylist, i)
                    #all_kw_scores.append(compute_topic_keyword_scores(sXarray, winds, doccategorylist, i))          
                    all_kw_scores.append(kw_scores_mean)          
                kw_scores = all_kw_scores[filecategory-1]

                #
                nsuggested_files = len(jsons)

                #Number of files having same category
                nsamecategory = 0.0

                #Print all tags of jsons
                for json in jsons:
                    print("Tags: ", json['tags'])
                    #Split file -tag for checking category
                    for ti, tag in enumerate(json['tags']):
                        if json['tags'][ti].split('=')[0] == "enron_category":
                            #
                            categoryid = int( json['tags'][ti].split('=')[1].split(':')[0] )
                            print("Category: ", categoryid)
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
                eps = 0.00001
                if sum(all_kw_scores) > 0:
                    print("Precisions: ",cprecision, avgprecision, 'kw_scores: ', kw_scores, 'normalized:', kw_scores/(sum(all_kw_scores)))
                    print("  ", all_kw_scores/(sum(all_kw_scores)))
                print("  ", kws,"\n")
                #
                precisionlist.append([cprecision, avgprecision, kw_scores/(sum(all_kw_scores)+eps)])

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
        #f = open('data/precisionlist_'+filename+'.list','w')
        #pickle.dump(precisionlist,f)
        pickle.dump(precisionlist, open('data/precisionlist_'+filename+'.list','wb'))










else:
    #Import loggerthreadq
    if sys.platform == "linux2":
      from loggerthread_linux import *
    elif sys.platform == "darwin":
      from loggerthread_osx import *
    else:
      print("Unsupported platform")
      sys.exit()

    #open()
    #metavar="filename", 
