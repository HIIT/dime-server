import email
from classes import *
from os import listdir, chdir
from retrieveEmails import *
from Topic_Modelling_Noun_Phrases import *
import sys

if __name__ == "__main__":
    ENRON = 0
    name_email_id = {'badeer-r':'robert.badeer@enron.com', 'causholli-m' :'monika.causholli@enron.com',  'guzman-m' :'mark.guzman@enron.com',  'keiser-k' :'kam.keiser@enron.com',   'may-l'  :'larry.may@enron.com',   'presto-k'	:'kevin.presto@enron.com',  'scholtes-d':'diana.scholtes@enron.com', 
    'benson-r' :'robert.benson@enron.com',  'corman-s' :'shelley.corman@enron.com',    'hain-m':'mary.hain@enron.com', 	'lay-k'	:'kenneth.lay@enron.com',     'mckay-b' :'brad.mckay@enron.com',  'quigley-d'	:'dutch.quigley@enron.com',  'taylor-m':'mark.taylor@enron.com', 
    'blair-l':'lynn.blair@enron.com',    'cuilla-m' :'martin.cuilla@enron.com',     'harris-s':'steven.harris@enron.com',   'lenhart-m':'matthew.lenhart@enron.com',   'neal-s':'scott.neal@enron.com',    'ring-r':'richard.ring@enron.com', 	 'whalley-g':'greg.whalley@enron.com', 
    'cash-m':'michelle.cash@enron.com', 	  'dickson-s' :'stacy.dickson@enron.com',    'heard-m':'marie.heard@enron.com', 	 'martin-t':'a..martin@enron.com',    'panus-s':'stephanie.panus@enron.com',   'rodrique-r' :'robin.rodrigue@enron.com',  'williams-w3':'bill.williams@enron.com'}
    
    if(len(sys.argv) > 1):
        conn = imaplib.IMAP4_SSL("imap.aalto.fi", 993)
        USERNAME =  sys.argv[1]
        em_id =  sys.argv[2]
        PASSWORD =  sys.argv[3]
        conn.login(USERNAME, PASSWORD)
        current_user = retrieveEmails(conn, em_id)
        k = len(sys.argv) - 4
        for i in range(4, len(sys.argv) ):
            getTopPhrases_list(current_user, sys.argv[i])
        topPhrases_NMF(current_user)    
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
        PASSWORD = keyring.get_password('my_Gmail',USERNAME)
        conn.login(USERNAME, PASSWORD)
        current_user = retrieveEmails(conn, em_id)
        print 'Organizations'
        getOrganizations(current_user)
        print 'Locations'
        getLocations(current_user)
        print 'People'
        getPeople(current_user)
        print 'Skills'
        getSkills(current_user)
        #getTimeStats(current_user)
        #getTopPhrases_list(current_user, "aristides.gionis@aalto.fi")
        #topPhrases_NMF(current_user)
        

