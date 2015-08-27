# -*- coding: iso-8859-15 -*-
import email
from classes import *
from os import listdir, chdir
from retrieveEmails import *
from Topic_Modelling_Noun_Phrases import *
import sys
from plotHist import *
import getpass
from datetime import datetime
if __name__ == "__main__":
    ENRON = 0
    name_email_id = {'badeer-r':'robert.badeer@enron.com', 'causholli-m' :'monika.causholli@enron.com',  'guzman-m' :'mark.guzman@enron.com',  'keiser-k' :'kam.keiser@enron.com',   'may-l'  :'larry.may@enron.com',   'presto-k'	:'kevin.presto@enron.com',  'scholtes-d':'diana.scholtes@enron.com', 
    'benson-r' :'robert.benson@enron.com',  'corman-s' :'shelley.corman@enron.com',    'hain-m':'mary.hain@enron.com', 	'lay-k'	:'kenneth.lay@enron.com',     'mckay-b' :'brad.mckay@enron.com',  'quigley-d'	:'dutch.quigley@enron.com',  'taylor-m':'mark.taylor@enron.com', 
    'blair-l':'lynn.blair@enron.com',    'cuilla-m' :'martin.cuilla@enron.com',     'harris-s':'steven.harris@enron.com',   'lenhart-m':'matthew.lenhart@enron.com',   'neal-s':'scott.neal@enron.com',    'ring-r':'richard.ring@enron.com', 	 'whalley-g':'greg.whalley@enron.com', 
    'cash-m':'michelle.cash@enron.com', 	  'dickson-s' :'stacy.dickson@enron.com',    'heard-m':'marie.heard@enron.com', 	 'martin-t':'a..martin@enron.com',    'panus-s':'stephanie.panus@enron.com',   'rodrique-r' :'robin.rodrigue@enron.com',  'williams-w3':'bill.williams@enron.com'}
    
    if(len(sys.argv) > 1):
        #domain = 'imap.aalto.fi'
        
        domain = sys.argv[1]
        conn = imaplib.IMAP4_SSL(domain, 993)
        USERNAME =  sys.argv[2]
        print USERNAME
        em_id =  sys.argv[3]
        print em_id
        PASSWORD =  getpass.getpass("Enter your Password:")
        conn.login(USERNAME, PASSWORD)
        start=datetime.now()
        since_date = sys.argv[4]
        if( since_date == ''):
            since_date = '01-JUN-2014'
        before_date = sys.argv[5]
        if( before_date == ''):
            before_date = '28-JUL-2015'
        k = len(sys.argv) - 6
        i_peer_list = []
        for i in range(6, len(sys.argv) ):
            i_peer_list.append(sys.argv[i])
        current_user = retrieveEmails(conn, em_id, since_date, before_date)
        file = open('email_mining_output_'+USERNAME+'.txt', 'w')
        getTopPhrases_list(current_user, i_peer_list, file)
        getAllStats(current_user,i_peer_list, file )
        print 'Top Phrases and Entities written into--' +'email_mining_output_'+USERNAME+'.txt'
        file.close()
        d = getAllStats_DF(current_user)
        times = pd.Series(d['times'])
        d['Seconds'] = (pd.to_timedelta(times,unit='d')+pd.to_timedelta(1,unit='s')).astype('timedelta64[s]')
        d.to_csv('Stats.csv')
        print 'Time and Text length stats written to Stats.csv File'
        print 'Total Time Elapased:',  datetime.now()-start
        #plotHist(log_t, 'Response Time (log seconds)', 'Number of Peers', 'log_Distribution.png')
        #plotHist(t, 'Response Time (seconds)', 'Number of Peers', 'Distribution.png')
        #topPhrases_NMF(current_user)    
    elif(ENRON == 1):
        users = []
        DIR = "/home/mallend1/Downloads/enron_mail/maildir"
        chdir(DIR)
        names = [d for d in listdir(".") if "." not in d]
        for name in names:
            chdir(DIR+'/'+name)
            print name
            person = name
            em_id = name_email_id[person]
            print person, em_id
            current_user = retrieveEmails_Enron(person, em_id)
            users.append(current_user)
            topPhrases(current_user)
        len(users)
    else:
        conn = imaplib.IMAP4_SSL("imap.aalto.fi", 993)
        USERNAME = 'mallend1'
        email_id = 'darshan.mallenahallishankaralingappa@aalto.fi' #user-id
        em_id = email_id
        PASSWORD = getpass.getpass()
        conn.login(USERNAME, PASSWORD)
        since_date = '01-JUN-2014'
        before_date = '13-AUG-2015'
        current_user = retrieveEmails(conn, em_id, since_date, before_date)
        #print '##############Organizations'
        #getOrganizations(current_user)
        #print '##############Locations'
        #getLocations(current_user)
        #print '##############People'
        #getPeople(current_user)
        #print '##############Skills'
        #getSkills(current_user)
        #print '##############Time and Text Length '
        #getTimeLengthStats(current_user)
        d = getAllStats_DF(current_user)
        times = pd.Series(d['times'])
        d['Seconds'] = (pd.to_timedelta(times,unit='d')+pd.to_timedelta(1,unit='s')).astype('timedelta64[s]')
        d.to_csv('DarshanStats.csv')
        #log_t = np.log(t)
        #plotHist(log_t, 'Response Time (log seconds)', 'Number of Peers', 'log_Distribution.png')
        #plotHist(t, 'Response Time (seconds)', 'Number of Peers', 'Distribution.png')
        #getTopPhrases_list(current_user, "aristides.gionis@aalto.fi")
        
        

