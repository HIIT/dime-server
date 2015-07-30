#!/usr/bin/python
# -*- coding: utf-8 -*-

#For keylogging
from fetch_keys_linux import *

#For searching from DiMe 
from dime_search import *

#For updating dictionary, topic_model and LinRel -matrix
from update_dict_lda_and_Am import *

#For GUI
from PyQt4 import QtCore, QtGui, uic
#
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Includes the definition of clickable label
from ExtendedQLabel import *

#For Rapid Automatic Keyword Extraction (RAKE)
import rake

#
import re

#For getting web page title
#import lxml.html
import urllib2
from BeautifulSoup import BeautifulSoup

# Definition of GUI
class Window(QtGui.QWidget):
    def __init__(self, val):
        QtGui.QWidget.__init__(self)

        #Read user.ini file
        self.srvurl, self.username, self.password, self.time_interval, self.nspaces, self.nw, self.updateinterval = self.read_user_ini()

        # mygroupbox.setLayout(myform)
        urlstrs = ''
        iconfile = 'web.png'
        self.gbtitle = 'Web sites'
        self.labellist, self.datelist = self.create_labellist(val, urlstrs)
        self.scrollarea = self.create_groupbox(self.gbtitle, self.labellist, self.datelist, iconfile)
        iconfile = 'mail.png'
        self.gbtitle2= 'E-mails'
        self.labellist2, self.datelist2 = self.create_labellist(val, urlstrs)
        self.scrollarea2 = self.create_groupbox(self.gbtitle2, self.labellist2, self.datelist2, iconfile)
        iconfile = 'doc.png'
        self.gbtitle3= 'Docs'
        self.labellist3, self.datelist3 = self.create_labellist(val, urlstrs)
        self.scrollarea3 = self.create_groupbox(self.gbtitle3, self.labellist3, self.datelist3, iconfile)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.scrollarea)
        layout.addWidget(self.scrollarea2)
        layout.addWidget(self.scrollarea3)

        self.setWindowTitle("ProActive Search")

    def create_labellist(self, val, urlstrs):
        labellist = []
        datelist = []
        if len(urlstrs) > 0:
          for i in range( len(urlstrs) ):
                          linkstr = str( urlstrs[i]["uri"] )
                          ctime   = str(urlstrs[i]["timeCreated"])
                          typestr = str(urlstrs[i]["type"])
                          storedas = str(urlstrs[i]["isStoredAs"])
                          #print ctime
                          timeint = int(ctime) / 1000
                          #print timeint
                          date = datetime.datetime.fromtimestamp(timeint)
                          datestr = date.__str__()

                          labellist[i].setText(linkstr)
                          datelist[i].setText(datestr)
                          storedasl = storedas.split('#')[1]
                          #if typestr in ['http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#PaginatedTextDocument', 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document']:
                          #print storedasl
                          if storedasl in ["LocalFileDataObject"]:
                              labellist3[j].setText(linkstr)
                              j = j + 1
        else:
          for i in range(val):
              #dumlabel = ExtendedQLabel('Hello')
              dumlabel = ExtendedQLabel()
              dumlabel.setAlignment(Qt.AlignLeft)
              dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)
              #labellist.append(QtGui.QLabel('mylabel'))
              labellist.append(dumlabel)

              datelist.append(QtGui.QLabel('date'))

        return labellist, datelist

    # def update_labellist(self, urlstrs):
    #     j=0

    #     labellist  = []
    #     labellist2 = []
    #     labellist3 = []
    #     datelist  = []
    #     datelist2 = []
    #     datelist3 = []
    #     if len(urlstrs) > 0:
    #       for i in range( len(urlstrs) ):
    #                       linkstr = str( urlstrs[i]["uri"] )
    #                       ctime   = str(urlstrs[i]["timeCreated"])
    #                       typestr = str(urlstrs[i]["type"])
    #                       storedas = str(urlstrs[i]["isStoredAs"])

    #                       dumlabel = ExtendedQLabel(linkstr, self)
    #                       dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)      

    #                       #print ctime
    #                       timeint = int(ctime) / 1000
    #                       #print timeint
    #                       date = datetime.datetime.fromtimestamp(timeint)
    #                       datestr = date.__str__()

    #                       labellist.append(dumlabel)
    #                       datelist.append(datestr)

    #                       storedasl = storedas.split('#')[1]
    #                       #if typestr in ['http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#PaginatedTextDocument', 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document']:
    #                       #print storedasl
    #                       if storedasl in ["LocalFileDataObject" ]:
    #                           dumlabel = ExtendedQLabel(linkstr, self)
    #                           dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)                                        
    #                           labellist3[j].setText(linkstr)
    #                           j = j + 1
    #     else:
    #       pass

    #     labellist2 = labellist
    #     datelist2 = datelist

    #     self.labellist = labellist
    #     self.labellist2= labellist2
    #     self.labellist3= labellist3

    #     self.datelist = datelist
    #     self.datelist2= datelist2
    #     self.datelist3= datelist3
    #     #return labellist, labellist2, labellist3, datelist, datelist2, datelist3


    def create_groupbox(self, gbtitle, labellist, datelist, iconfile):
        mygroupbox = QtGui.QGroupBox(gbtitle)
        #myform = QtGui.QFormLayout()
        myform = QtGui.QVBoxLayout()
        combolist = []

        #
        for i in range(len(labellist)):
            #dumlabel = ExtendedQLabel('Hello', self)
            #dumlabel.connect(dumlabel, SIGNAL('clicked()'), dumlabel.open_url)
            #self.labellist.append(dumlabel)

            datelist.append(QtGui.QLabel('date'))

            #
            image = QtGui.QImage(iconfile)
            icon = QtGui.QPixmap.fromImage(image)
            icon = icon.scaledToHeight(20)
            
            label1 = QtGui.QLabel('Hello')

            label1.setPixmap(icon)
            label2 = QtGui.QLabel('test_urls')
            #label2.setPicture(picture)
            
            boxl = QtGui.QHBoxLayout()
            boxl.setSpacing(10)
            boxl.addWidget(label1, Qt.AlignLeft)
            boxl.addWidget(labellist[i], Qt.AlignLeft)
            boxl.addWidget(datelist[i], Qt.AlignLeft)
            boxl.addStretch(10)
            myform.addItem(boxl)
            # #grid = QtGui.QGridLayout()
            # grid.setSpacing(2)
            # grid.addWidget(label1,1,0, Qt.AlignLeft)
            # #grid.setHorizontalSpacing(1)
            # grid.addWidget(labellist[i],1,1,Qt.AlignLeft)
            # #grid.addWidget(datelist[i],1,2, Qt.AlignRight)
            # myform.addItem(grid)
            # #myform.addRow(labellist[i])
        
        mygroupbox.setLayout(myform)

        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidget(mygroupbox)
        scrollarea.setWidgetResizable(True)
        
        return scrollarea
        #return mygroupbox 


    def update_groupbox(self, iconfile):
        mygroupbox = QtGui.QGroupBox(self.gbtitle)
        myform = QtGui.QFormLayout()
        #self.labellist = []
        #self.datelist = []
        combolist = []

        #
        for i in range(len(self.labellist)):
            #self.datelist[i] = '20.09.2015'

            #
            image = QtGui.QImage(iconfile)
            icon = QtGui.QPixmap.fromImage(image)
            icon = icon.scaledToHeight(20)
            label1 = QtGui.QLabel('')
            label1.setPixmap(icon)

            #label2.setPicture(picture)
            grid = QtGui.QGridLayout()
            grid.setSpacing(10)
            grid.addWidget(label1,1,0)
            grid.addWidget(self.labellist[i],1,1)
            grid.addWidget(QtGui.QLabel('Date'),1,2)
            myform.addItem(grid)
            #myform.addRow(labellist[i])
        
        mygroupbox.setLayout(myform)

        scrollarea = QtGui.QScrollArea()
        scrollarea.setWidget(mygroupbox)
        scrollarea.setWidgetResizable(True)
        
        self.scrollarea = scrollarea

    def startlog(self):
        threading.Thread(target = log, args = (self,) ).start()

    def show_link(self):
        threading.Thread(target = update_visible_link, args = (self,)).start()

    def update_links(self, urlstr):
      #for i in len(r.json())
      if urlstr != None:
        nsuggestedlinks = len(urlstr.json())
        nlinks          = len(self.labellist)
        if nsuggestedlinks <= nlinks:
          for i in range( len(urlstr.json()) ):
            linkstr = str( urlstr.json()[i]["uri"] )
            self.labellist[i].setText(linkstr)
            plaintext    = urlstr.json()[i]["plainTextContent"]
            tooltipstr   = re.sub("[^\w]", " ", plaintext)
            self.labellist[i].setToolTip(tooltipstr[0:120])

    def update_links3(self, urlstrs):
        i = 0
        j = 0

        #Initialize rake object
        rake_object = rake.Rake("SmartStoplist.txt", 5, 5, 4)

        if urlstrs != None:
             nsuggestedlinks = len(urlstrs)
             nlinks = len(self.labellist)
        nlinks = len(self.labellist)
        nsuggestedlinks = 5
        if nsuggestedlinks <= nlinks:
                    #for i in range( len(self.labellist) ):
                    for i in range( len(urlstrs) ):
                                    linkstr  = str( urlstrs[i]["uri"] )
                                    ctime    = str(urlstrs[i]["timeCreated"])
                                    typestr  = str(urlstrs[i]["type"])
                                    storedas = str(urlstrs[i]["isStoredAs"])
                                    storedasl = storedas.split('#')[1]
                                    content  = urlstrs[i]["plainTextContent"]
                                    keywords = rake_object.run(content)
                                    #print ctime
                                    timeint = int(ctime) / 1000
                                    #print timeint
                                    date = datetime.datetime.fromtimestamp(timeint)
                                    datestr = date.__str__()

                                    if len(linkstr) > 20:
                                      linkstrshort = linkstr[0:40]
                                    

                                    if len(keywords) > 0:
                                      tooltipstr = re.sub("[^\w]", " ", content)
                                      #self.labellist[i].setToolTip(tooltipstr)
                                      keywordstr = "Keywords: " + keywords[0][0]
                                    else:
                                      keywordstr = 'Keywords: '
                                      #self.labellist[i].setText(keywords[0][0])

                                    #if typestr in ['http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#PaginatedTextDocument', 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document']:
                                    print storedasl
                                    if storedasl in ["LocalFileDataObject" ]:
                                        self.labellist3[j].setText(linkstrshort)
                                        self.labellist3[j].uristr = linkstr
                                        self.labellist3[j].setToolTip(keywordstr)
                                        self.datelist3[j].setText(datestr)
                                        #self.labellist3[j].setAlignment(Qt.AlignLeft)

                                        j = j + 1
                                    else:
                                        #t = lxml.html.parse(linkstr)
                                        #title = t.find(".//title").text
                                        #if linkstr.split('//')[0] == 'http:' or linkstr.split('//')[0] == 'https:':
                                      title = None
                                      try:
                                        dumt = urllib2.urlopen(linkstr)
                                        soup = BeautifulSoup(dumt)
                                        try: 
                                          if soup.title is not None:
                                            title = soup.title.string
                                        except AttributeError or ValueError:  
                                          #print 'attr. error'
                                          pass
                                      except urllib2.HTTPError or urllib2.URLError or ValueError:
                                        pass

                                      if title is None:
                                        title = linkstrshort

                                      # try:
                                      #   dumt = urllib2.urlopen(linkstr)
                                      #   soup = BeautifulSoup(dumt)
                                      #   title = soup.title.string
                                      # except urllib2.HTTPError:
                                      #   title = linkstrshort

                                      self.labellist[i].setText(title)
                                      self.labellist[i].uristr = linkstr
                                      self.labellist[i].setToolTip(keywordstr)
                                      self.datelist[i].setText(datestr)
                                        


    def read_user_ini(self):

        f          = open('user.ini','r')
        dumstr     = f.read()
        stringlist = dumstr.split()

        for i in range( len(stringlist) ):
                if stringlist[i] == "server_url:":
                        srvurl = stringlist[i+1]
                if stringlist[i] == "usrname:":
                        usrname = stringlist[i+1]
                if stringlist[i] == "password:":
                        password = stringlist[i+1]
                if stringlist[i] == "time_interval:":
                        time_interval_string = stringlist[i+1]
                        time_interval = float(time_interval_string)
                if stringlist[i] == "nspaces:":
                        nspaces_string = stringlist[i+1]
                        nspaces = int(nspaces_string)
                if stringlist[i] == "numwords:":
                        dum_string = stringlist[i+1]
                        numwords = int(nspaces_string)                      
                if stringlist[i] == "updating_interval:":
                        dum_string = stringlist[i+1]
                        updateinterval = float(dum_string)                        

        return srvurl, usrname, password, time_interval, nspaces, numwords, updateinterval

    #
    def open_url(self):
      global urlstr
      webbrowser.open(urlstr)

    #
    def stopstart(self):
      global var

      if var == True:
	      var = False
	      self.ssbutton.setText("Start logging")
	      self.ssbutton.setStyleSheet("background-color: lightGreen")
	      self.statuslabel.setText("Logging disabled")
	      self.statuslabel.setStyleSheet("color: red")
      elif var == False:
	      var = True
	      self.ssbutton.setText("Stop logging")
	      self.ssbutton.setStyleSheet("color: red")
	      self.statuslabel.setText("Logging ongoing")
	      self.statuslabel.setStyleSheet("color: green")
	      #self.statuslabel.setStyleSheet("background-color: lightRed")
              self.startlog()

    def quitting(self):
      global var
      var = False
      QtCore.QCoreApplication.instance().quit()

    #Quit
    def closeEvent(self, event):
        self.quitting()


################################################################

###
def log(win):
      #Number 
      numoftopics = 10

      #List of urls
      urlstr = []

      #global urlstr
      global var

      countspaces = 0
      sleep_interval = 0.005

      #starttime = datetime.datetime.now().time().second
      now = time()
      flag = 0
      flag2= 0
      dumstr = ''
      wordlist = []

      #Before searching, update data
      update_data(win.srvurl, win.username, win.password)
      update_dictionary()
      update_doctm()
      update_doc_tfidf_list()
      #spielberg 
      # if os.path.isfile('/tmp/tmpldamodel'):
      #   update_topic_model_and_doctid()
      # else:
      #   create_topic_model_and_doctid(numoftopics)
      #update_topic_keywords()
      update_docsim_model()
      #update_X()
      update_Xt_and_docindlist([0])

      print "Ready for logging"

      #f = open('typedwords.txt', 'a')
      while var:

        #sleep(sleep_interval)
        changed, modifiers, keys = fetch_keys()
	      #print changed, modifiers, keys
        keys  = str(keys)

        #Take care that ctrl is not pressed at the same time
        if not (modifiers['left ctrl'] or modifiers['right ctrl']):
          #Take current time
          cdate = datetime.datetime.now().date()
          ctime = datetime.datetime.now().time()

          cmachtime = time()
          var2 = cmachtime > now + float(win.time_interval)
          var3 = cmachtime > now + float(win.updateinterval)

          if keys == 'None':
                  keys = ''

          elif keys == '<backspace>':
                  keys = ''
                  #Convert current string into list of characters
                  duml = list(dumstr)
                  if len(duml) > 0:
                          #Delete the last character from the list
                          del( duml[len(duml)-1] )
                          #Convert back to string
                          dumstr = "".join(duml)

          elif keys in ['<enter>', '<tab>','<right ctrl>','<left ctrl>'," "]:

                  #keys = ' '
                  wordlist.append(dumstr)
                  #dumstr = dumstr + keys
                  countspaces = countspaces + 1
                  dumstr = ''

                  if var2:
                          if var3: 
                            #Update stuff
                            update_data(win.srvurl, win.username, win.password)
                            update_dictionary()
                            update_doctm()
                            update_docsim_model()
                            #update_X()
                            update_Xt_and_docindlist([0])                           
                          #
                          dumstr2 = ''
                          for i in range( len(wordlist) ):
                                 dumstr2 = dumstr2 + wordlist[i] + ' '

                          #
                          f = open("typedwords.txt","a")
                          #print str(cdate) + ' ' + str(ctime) + ' ' + dumstr2 + '\n'
                          f.write(str(cdate) + ' ' + str(ctime) + ' ' + dumstr2 + '\n')
                          f.close()

                          #Make query to DiMe
                          #urlstr = search_dime(win.srvurl, win.username, win.password, dumstr2)
                          #urlstr = search_dime_lda(dumstr2)
                          #urlstr = search_dime_linrel(dumstr2)
                          #urlstr, docinds = search_dime_docsim(dumstr2)
                          #urlstr = search_dime_linrel(dumstr2)
                          urlstr = search_dime_linrel_summing_previous_estimates(dumstr2)


                          #iconfile = 'web.png'

                          #win.update_groupbox(iconfile)
                          if len(urlstr) > 0:
                            win.update_links3(urlstr)

                          print 'Ready for logging!'
                          #Add the suggested url into a history file
                          #if urlstr != None:
                          if len(urlstr) > 0:
                            f2 = open("suggested_pages.txt","a")
                            f2.write(str(cdate) + ' ' + str(ctime) + ' ' + str(urlstr[0]["uri"]) + '\n')
                            f2.close()

                          #Clear the dummy string
                          dumstr = ''
                          dumstr2= ''

                          #Remove content from wordlist
                          del wordlist[:]

                          countspaces = 0

                          flag = 1
                          flag2= 0

                          now = time()

          else:
                  cdate = datetime.datetime.now().date()
                  ctime = datetime.datetime.now().time()
                  dumstr = dumstr + keys

####################################################################


if __name__ == "__main__":

  #Important global variables!
  global urlstr
  #Initialize urlstr
  #urlstr = search_dime("petrihiit","p3tr1h11t","python")

  global var
  var = True

  #Make the QGui.QApplication object
  app = QtGui.QApplication(sys.argv)
  #Set Taskbar icon for app object
  app.setWindowIcon(QtGui.QIcon('keyboard.png'))

  #Get screen dimensions
  screen = app.desktop()
  sl = screen.width()
  sh = screen.height()

  #Make a WindowClass object
  newwindow = Window(5)

  #Make window frameless
  #newwindow.setWindowFlags(QtCore.Qt.CustomizeWindowHint)

  newwindow.show()

  #Move the window into the right corner
  newwindow.move(sl-350,0)


  #Determine the dimensions
  width = round(sl*0.5)
  newwindow.resize(width, 50)

  #Start keylogger
  newwindow.startlog()

  #Start
  app.exec_()
