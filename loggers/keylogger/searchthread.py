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
import Queue
import threading

from update_files import *

from dime_search import *

#Includes the definition of clickable label
from ExtendedQLabel import *

#For getting web page title
#import lxml.html
import urllib2
#from BeautifulSoup import BeautifulSoup

#
import re

#
import math

#For checking data types
import types

#
class SearchThread(QThread):

 send_links = pyqtSignal(list)
 send_keywords = pyqtSignal(list)
 start_search = pyqtSignal()
 all_done = pyqtSignal()
 
 def __init__(self):
  QThread.__init__(self)
  self.query = ''
  self.oldquery  = None
  self.oldquery2 = None
  self.searchfuncid = 0
  self.extrasearch = False
  #Exploration/Exploitation -coefficient
  self.c          = 0.0

  #DiMe server path, username and password
  self.srvurl, self.usrname, self.password, self.time_interval, self.nspaces, self.numwords, self.updateinterval, self.data_update_interval, self.nokeypress_interval = read_user_ini()
  self.dataupdateinterval = 600

  #
  json_data = open('data/json_data.txt')
  #DiMe data in json -format
  self.data       = json.load(json_data)
  #Load df-matrix (document frequency matrix)
  self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')
  #Load dictionary
  self.dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
  #Remove common words from dictionary
  self.dictionary = df_word_removal(self.sXdoctm, self.dictionary)
  #Load updated tfidf-matrix of the corpus
  self.sX         = load_sparse_csc('data/sX.sparsemat.npz')
  #Load updated df-matrix
  self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')      
  #Load tfidf -model
  self.tfidf      = models.TfidfModel.load('data/tfidfmodel.model')
  #Load 
  self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')
  #Load tfidf -model
  self.tfidf      = models.TfidfModel.load('data/tfidfmodel.model')
  #Load cosine similarity model for computing cosine similarity between keyboard input with documents
  self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')

  if os.path.isfile('data/r_old.npy'):
    os.remove('data/r_old.npy')


 def __del__(self):
   self.wait()

 def change_search_function(self, searchfuncid):
  self.searchfuncid = searchfuncid
  print 'Search thread: search function changed to', str(searchfuncid)
  if searchfuncid == 1 or searchfuncid == 2 or searchfuncid == 3:
    #Update LinRel data files
    print 'Search thread: Updating Linrel data files!!!'
    print 'Search thread: path: ', os.getcwd()
    #check_update()

 def get_new_c(self, value):
  #print "Search thread: new c value: ", value
  self.c = math.log(value+1)

 def recompute_keywords(self,value):
  print value
  self.c = math.log(value+1)
  kws = recompute_keywords(math.log(value+1))
  self.send_keywords.emit(kws)

 def get_new_word(self, newquery):
  #newquer is a QString, so it has to be changed to a unicode string
  #print "XXX", type(newquery)
  #asciiquery = newquery.toAscii()
  #Convert to Unicode
  #newquery = unicode(asciiquery, 'utf-8')
  #newquery = unicode(newquery)
  print "Search thread: got new query from logger:", newquery
  self.query = newquery

 def get_new_word_from_main_thread(self, keywords):
  if self.query is None:
    self.query = ''
  #
  #utf8keyword = keywords.toUtf8()
  #print 'ASCII KEYWORD: ', utf8keyword
  #keywords = unicode(utf8keyword, 'utf-8')
  self.query = self.query + ' ' + keywords

  print "Search thread: got new query from main:", self.query
  self.extrasearch = True

 def run(self):
   self.search()

 def search(self):

  #nokeypress_interval = 5.0
  timestamp = time()
  dataupdatetimestamp = time()

  #Check that all data files exist
  check_update()


  while True:
    #
    cmachtime = time()

    #Update data
    if cmachtime > self.dataupdateinterval + dataupdatetimestamp:
      print "Update data!!!!!"
      #update_all_data()
      dataupdatetimestamp = time()
      #
      json_data = open('data/json_data.txt')
      #DiMe data in json -format
      self.data       = json.load(json_data)
      #Load df-matrix (document frequency matrix)
      self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')
      #Load dictionary
      self.dictionary = corpora.Dictionary.load('/tmp/tmpdict.dict')
      #Remove common words from dictionary
      self.dictionary = df_word_removal(self.sXdoctm, self.dictionary)
      #Load updated tfidf-matrix of the corpus
      self.sX         = load_sparse_csc('data/sX.sparsemat.npz')
      #Load updated df-matrix
      self.sXdoctm    = load_sparse_csc('data/sXdoctm.sparsemat.npz')      
      #Load tfidf -model
      self.tfidf      = models.TfidfModel.load('data/tfidfmodel.model')
      #Load 
      self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')
      #Load tfidf -model
      self.tfidf      = models.TfidfModel.load('data/tfidfmodel.model')
      #Load cosine similarity model for computing cosine similarity between keyboard input with documents
      self.index      = similarities.docsim.Similarity.load('/tmp/similarityvec')
      #Clean the history buffer
      if os.path.isfile('data/r_old.npy'):
        os.remove('data/r_old.npy')


    #
    if self.extrasearch:
      print 'Search thread: got extra search command from main!'      
      jsons, docinds = search_dime_docsim(dstr, self.data, self.index, self.dictionary)
      self.extrasearch = False    

    #
    if self.query is not None and self.query != self.oldquery2:
      #print 'self.query!!!!!'
      timestamp = time()
      self.oldquery2 = self.query

    #print "Query:", self.query, "Oldquery:", self.oldquery
    #if self.query is not None and self.query != self.oldquery:
    if self.query is not None and self.query != self.oldquery and cmachtime > timestamp + self.nokeypress_interval:
      dstr = self.query      
      print 'Search thread:', dstr
        #dstr = unicode(dstr, 'utf-8')

      self.start_search.emit()
      if self.searchfuncid == 0:
        jsons, docinds = search_dime_docsim(dstr, self.data, self.index, self.dictionary)
        print 'Search thread: Ready for new search!'
      elif self.searchfuncid == 1:
        #Create/update relevant data files if necessary and store into 'data/' folder in current path batman 
        #jsons, kws = search_dime_linrel_summing_previous_estimates(dstr)
        jsons, kws = search_dime_linrel_keyword_search_dime_search(dstr, self.sX, self.tfidf, self.dictionary, self.c, self.srvurl, self.usrname, self.password)
        print 'Search thread: Ready for new search!'
        print len(jsons)
        if len(jsons) > 0:
          #Return keyword list
          self.send_keywords.emit(kws)
      elif self.searchfuncid == 2:
        #Create/update relevant data files if necessary and store into 'data/' folder in current path batman 
        jsons = search_dime_linrel_without_summing_previous_estimates(dstr)
        print 'Search thread: Ready for new search!'   
      elif self.searchfuncid == 3:
        #Create/update relevant data files if necessary and store into 'data/' folder in current path batman 
        #jsons, kws = search_dime_linrel_keyword_search(dstr, self.sX, self.tfidf, self.dictionary, self.c)
        jsons, kws = search_dime_linrel_keyword_search(dstr, self.sX, self.data, self.index, self.tfidf, self.dictionary, self.c)
        if len(jsons) > 0:
          #Return keyword list
          self.send_keywords.emit(kws)
        print 'Search thread: Ready for new search!'      

      print 'Search thread: len jsons ', len(jsons)
      if len(jsons) > 0:
        #Return keyword list
        #self.emit( QtCore.SIGNAL('finished(PyQt_PyObject)'), kws)
        #Return jsons
        self.send_links.emit(jsons)

        #Write first url's appearing in jsons list to a 'suggested_pages.txt'
        cdate = datetime.datetime.now().date()
        ctime = datetime.datetime.now().time()
        f = open("suggested_pages.txt","a")
        f.write(str(cdate) + ' ' + str(ctime) + ' ' + str(jsons[0]["uri"]) + '\n')
        f.close()
      self.oldquery = dstr
      self.all_done.emit()


    else:
      sleep(0.3) # artificial time delay    



 # def read_user_ini():

 #    #
 #    f          = open('user.ini','r')
 #    dumstr     = f.read()
 #    stringlist = dumstr.split()

 #    for i in range( len(stringlist) ):
 #            if stringlist[i] == "server_url:":
 #                    srvurl = stringlist[i+1]
 #            if stringlist[i] == "usrname:":
 #                    usrname = stringlist[i+1]
 #            if stringlist[i] == "password:":
 #                    password = stringlist[i+1]
 #            if stringlist[i] == "time_interval:":
 #                    time_interval_string = stringlist[i+1]
 #                    time_interval = float(time_interval_string)
 #            if stringlist[i] == "nspaces:":
 #                    nspaces_string = stringlist[i+1]
 #                    nspaces = int(nspaces_string)
 #            if stringlist[i] == "numwords:":
 #                    dum_string = stringlist[i+1]
 #                    numwords = int(dum_string)                      
 #            if stringlist[i] == "updating_interval:":
 #                    dum_string = stringlist[i+1]
 #                    updateinterval = float(dum_string)  
 #            if stringlist[i] == "data_update_interval:":
 #                dum_string = stringlist[i+1]
 #                data_update_interval = float(dum_string)
 #            if stringlist[i] == "nokeypress_interval:":
 #                dum_string = stringlist[i+1]
 #                nokeypress_interval = float(dum_string)

 #    return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval, data_update_interval, nokeypress_interval



 
 # def read_user_ini(self):

 #    f          = open('user.ini','r')
 #    dumstr     = f.read()
 #    stringlist = dumstr.split()

 #    for i in range( len(stringlist) ):
 #            if stringlist[i] == "server_url:":
 #                    srvurl = stringlist[i+1]
 #            if stringlist[i] == "usrname:":
 #                    usrname = stringlist[i+1]
 #            if stringlist[i] == "password:":
 #                    password = stringlist[i+1]
 #            if stringlist[i] == "time_interval:":
 #                    time_interval_string = stringlist[i+1]
 #                    time_interval = float(time_interval_string)
 #            if stringlist[i] == "nspaces:":
 #                    nspaces_string = stringlist[i+1]
 #                    nspaces = int(nspaces_string)
 #            if stringlist[i] == "numwords:":
 #                    dum_string = stringlist[i+1]
 #                    numwords = int(dum_string)                      
 #            if stringlist[i] == "updating_interval:":
 #                    dum_string = stringlist[i+1]
 #                    updateinterval = float(dum_string)                        

 #    return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval  


#def unicode_to_str(ustr):
#  """Converts unicode strings to 8-bit strings."""
#  try:
#      return ustr.encode('utf-8')
#  except UnicodeEncodeError:
#      print "Main: UnicodeEncodeError"
#  return ""
