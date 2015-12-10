#import sys, time
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5 import QtGui

# For Keylogger
import sys
import datetime #For import date and time
from time import sleep, time
import ctypes as ct
from ctypes.util import find_library

import os
import queue
import threading

from update_files import *

from dime_search2 import *

#Includes the definition of clickable label
#from ExtendedQLabel import *

#For getting web page title
#import lxml.html
import urllib.request, urllib.error, urllib.parse
#from BeautifulSoup import BeautifulSoup

#
import re

#
import math

#For checking data types
import types


####################################################
def get_item_id(json_item):
    if 'uri' in json_item:
        return json_item['uri']
    return None
####################################################

#
class SearchThread(QThread):

 #Signals
 send_links = pyqtSignal(list, list)
 send_keywords = pyqtSignal(list)
 send_query_string_and_corresponding_relevance_vector = pyqtSignal(list)
 start_search = pyqtSignal()
 all_done = pyqtSignal()
 
 def __init__(self):
  QThread.__init__(self)
  self.query = ''
  self.oldquery  = None
  self.oldquery2 = None
  self.searchfuncid = 0
  #Mode by which the relevance vector is determined from written/clicked input
  self.emphasize_kws = 0
  self.extrasearch = False
  self.old_search  = False
  #Exploration/Exploitation -coefficient
  self.c          = 0.0
  self.mmr_lambda = -1.0
  self.servertype = "dime"

  #DiMe server path, username and password
  self.srvurl, self.usrname, self.password, self.time_interval, self.nspaces, self.numwords, self.updateinterval, self.data_update_interval, self.nokeypress_interval, self.mu, self.n_results = read_user_ini()
  self.dataupdateinterval = 600

  #
  json_data = open('data/json_data.txt')
  
  #DiMe data in json -format
  #self.data       = json.load(json_data)
  
  #Load df-matrix (document frequency matrix)
  #self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')
  #print("Search thread: Size of a loaded tfidf matrix ",self.sXdoctm.data.nbytes)
  
  #Load dictionary
  self.dictionary = corpora.Dictionary.load('data/tmpdict.dict')
  
  #Remove common words from dictionary
  #df_word_removal(self.sXdoctm, self.dictionary)
  #self.dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
  
  #Load updated tfidf-matrix of the corpus
  self.sX         = load_sparse_csc('data/sX.sparsemat.npz')
  
  #Load updated df-matrix
  #self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')      
    
  #Load cosine similarity model for computing cosine similarity between keyboard input with documents
  #self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')
  self.index      = similarities.docsim.Similarity.load('data/similarityvec')

  #
  self.iteration_list = []


  if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')


 def __del__(self):
   self.wait()

 def change_search_function(self, searchfuncid):
  self.searchfuncid = searchfuncid
  print('Search thread: search function changed to', str(searchfuncid))
  if searchfuncid == 1 or searchfuncid == 2 or searchfuncid == 3:
    #Update LinRel data files
    print('Search thread: Updating Linrel data files!!!')
    print('Search thread: path: ', os.getcwd())
    #check_update()

 def get_new_c(self, value):
  #print "Search thread: new c value: ", value
  self.c = math.log(value+1)

 def recompute_keywords(self,value):
  #print(value)
  self.c = math.log(value+1)
  print("Exploration/Exploitation value: ",self.c)
  #kws = recompute_keywords(math.log(value+1))
  kws = recompute_keywords(self.c)
  self.send_keywords.emit(kws)

 def get_new_word(self, newquery):
  #newquer is a QString, so it has to be changed to a unicode string
  #print "XXX", type(newquery)
  #asciiquery = newquery.toAscii()
  #Convert to Unicode
  #newquery = unicode(asciiquery, 'utf-8')
  #newquery = unicode(newquery)
  newquery = newquery.strip() # to get rid of extra spaces, enters
  print("Search thread: got new query from logger: %s" % newquery)
  self.query = newquery


 #
 def clear_query_string(self):
  self.query = ''
  print("searchthread: query string cleared!!")

 
 #
 def get_new_word_from_main_thread(self, keywords):
  if self.query is None:
    self.query = ''
  #
  #utf8keyword = keywords.toUtf8()
  #print 'ASCII KEYWORD: ', utf8keyword
  #keywords = unicode(utf8keyword, 'utf-8')
  self.query = self.query + ' ' + keywords

  print("Search thread: got new query from main:", self.query)
  self.extrasearch = True


 #
 def get_explicit_query_from_main_thread(self, query_from_main):
  if query_from_main is None:
    self.query = ''
  else: 
    self.query = query_from_main
  print("Search thread: got explicit query from main:", self.query)

 #
 def get_old_query_from_main_thread(self, old_query_and_corresponding_relevance_vector):  
  #
  if self.query is None:
    self.query = ''
  #
  self.query = old_query_and_corresponding_relevance_vector[0]
  self.old_r = old_query_and_corresponding_relevance_vector[1]
  #
  print("Search thread: got old query from main:", self.query)
  self.old_search = True  

 def run(self):
   self.search()

 def search(self):

  #nokeypress_interval = 5.0
  timestamp = time()
  dataupdatetimestamp = time()

  #Check that all data files exist
  check_update()

  #
  i = 0
  iteration = {}

  #
  while True:

    #
    cmachtime = time()

    #Update data
    if cmachtime > self.dataupdateinterval + dataupdatetimestamp:
      print("Update data!!!!!")
      #update_all_data()
      dataupdatetimestamp = time()
      #
      json_data = open('data/json_data.txt')
      #DiMe data in json -format
      #self.data       = json.load(json_data)
      #Load df-matrix (document frequency matrix)
      #self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')
      #Load dictionary
      self.dictionary = corpora.Dictionary.load('data/tmpdict.dict')
      #Remove common words from dictionary
      #df_word_removal(self.sXdoctm, self.dictionary)
      #self.dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
      #Load updated tfidf-matrix of the corpus
      self.sX         = load_sparse_csc('data/sX.sparsemat.npz')
      #Load updated df-matrix
      #self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')      
      
      #Load 
      #self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')
      self.index      = similarities.docsim.Similarity.load('data/similarityvec')
      
      #Load cosine similarity model for computing cosine similarity between keyboard input with documents
      #self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')
      self.index      = similarities.docsim.Similarity.load('data/similarityvec')
      #Clean the history buffer
      if os.path.isfile('data/r_old.npy'):
        os.remove('data/r_old.npy')


    #
    if self.extrasearch:
      #
      print('Search thread: got extra search command from main!')      
      #
      #iteration['click'] = dstr
      parts = self.query.split()
      if(len(parts)>1):
        iteration['click'] = parts[-1]
        print("ITER 1",iteration, self.query)

      #jsons = search_dime(self.srvurl, self.usrname, self.password, dstr, self.n_results)

      #
      self.extrasearch = False

 
    #
    if self.query is not None and self.query != self.oldquery2:
      #print 'self.query!!!!!'
      timestamp = time()
      self.oldquery2 = self.query

    #If the query has changed, and certain amount of time in determined self.nokeypress_interval has expired, 
    #do the following:
    if self.query is not None and self.query != self.oldquery and cmachtime > timestamp + self.nokeypress_interval:

      #
      print("ITER 2",iteration, self.query)
      
      #Add to dstr the content of query text
      dstr = self.query      
      #print('Search thread: QUERY: ', dstr)

      #
      iteration['write'] = dstr

      #
      iteration['input'] = dstr

      #Send signal to GUI that the search has begun
      self.start_search.emit()

      solrdata = []
      #
      if not self.old_search:
        if self.searchfuncid == 0:
          print('Search thread: Does nothing!')
        elif self.searchfuncid == 1:
          #Search from dime using written input and do LinRel keyword computation
          dimedata, solrdata, kws, winds, vsum, r = search_dime_linrel_keyword_search_dime_search(dstr, self.sX, self.dictionary, self.c, self.mu, self.srvurl, self.usrname, self.password, self.n_results, emphasize_kws=self.emphasize_kws, servertype=self.servertype)
          #Send query text and its corresponding relevance vector
          self.send_query_string_and_corresponding_relevance_vector.emit([self.query, r])
        elif self.searchfuncid == 2:
          #Determine number of keywords to be added to the query
          n_query_kws = 10
          #Search from DiMe using the written text input and keywords
          dimedata, kws, winds, vsum, r = search_dime_using_linrel_keywords(dstr, n_query_kws, self.sX, self.dictionary, self.c, self.mu, self.srvurl, self.usrname, self.password, self.n_results, emphasize_kws=self.emphasize_kws, servertype=self.servertype)
          #Send query text and its corresponding relevance vector
          self.send_query_string_and_corresponding_relevance_vector.emit([self.query, r])
      #
      elif self.old_search:
        print("Do OLD SEARCH and then continue.")
        #
        dimedata, kws, winds, vsum, r = repeat_old_search(self.query, self.old_r, self.sX, self.dictionary, self.c, self.mu, self.srvurl, self.usrname, self.password, self.n_results, servertype=self.servertype)
        self.old_search = False        

      # elif self.searchfuncid == 3:
      #   #dimedata, kws = search_dime_linrel_keyword_search(dstr, self.sX, self.data, self.index, self.dictionary, self.c, self.mu)


      #If MMR enable, do MMR-reranking of kws
      if self.mmr_lambda > 0:
          frac_sizeS = 0.003
          frackws = 0.003
          kws_rr, winds_rr, mmr_scores = mmr_reranking_of_kws(self.mmr_lambda, winds, kws, vsum, frac_sizeS, self.sX, frackws)
          #kws, winds_re = mmr_reranking_of_kws(self.mmr_lambda, winds, kws, vsum, frac_sizeS, sX, frackws)
          print("RERANKED KEYWORDS with lambda=",self.mmr_lambda,":")

          if(len(vsum)>0 and len(mmr_scores)>0):
              #print(len(vsum))
              vsum_rr = []
              for wind in winds_rr[0:20]:
                  ind = winds.index(wind)
                  vsum_rr.append(vsum[ind])

              #print(mmr_scores)
              for di in range(20):
                  #
                  #print(kws_rr[di], mmr_scores[di], vsum_rr[di])

                  #Store the MMR- and LinRel scores (stored in 'vsum') of keywords
                  iteration['kws'] = {}
                  for l,kw in enumerate(kws):
                    iteration['kws'][kws_rr[di]] = [mmr_scores[di][0], vsum_rr[di][0]]

          #Substitute the reranked kws_rr to LinRel ranked kws
          kws = kws_rr
          winds = winds_rr

      print('Search thread: Ready for new search!')
      print('Search thread: len(dimedata)={0}, len(solrdata)={0} '.format(len(dimedata), len(solrdata)))
      if len(dimedata) > 0 or len(solrdata) > 0:

          #Send dimedata
          self.send_links.emit(dimedata, solrdata)
          #Send keywords
          self.send_keywords.emit(kws)

          #Write first url's appearing in dimedata to 'suggested_pages.txt'
          if self.servertype in ["dime", "both"] and len(dimedata) > 0:
              cdate = datetime.datetime.now().date()
              ctime = datetime.datetime.now().time()
              f = open("suggested_pages.txt","a")
              f.write(str(cdate)+' '+str(ctime)+' '+str(dimedata[0]["uri"])+'\n')
              f.close()

      #
      self.oldquery = dstr

      #Send signal to Main thread that search is done
      self.all_done.emit()

      #Print 'iteration' dict
      #print(iteration)

      #
      i = i + 1
      #
      iteration = {}
      iteration['i'] = i


    else:
      sleep(0.3) # artificial time delay    
