# -*- coding: iso-8859-15 -*-
import email
import os
import os.path
import sys
import numpy
import re
from collections import *
import pandas
from pandasql import *
import string
import imaplib
import keyring
from parseMail import *
from textblob import TextBlob
import html2text
import quotequail
from classes import *
from dateUtils import *
import EFZP as zp
import ner
from Topic_Modelling_Noun_Phrases import *
from skills_tree import *
from textUtils import *
from datetime import datetime
#conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
# Log In
h = html2text.HTML2Text()
h.ignore_links = True
# Regex patterns to remove to escape sequences and other characters from the email-id
regex = re.compile(r'[ \n\r\t\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]')
regex_1 = re.compile(r'[\n\r\t\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]')
re_fw_pattern =re.compile( '([\[\(] *)?(RE|FWD?) *([-:;)\]][ :;\])-]*|$)|\]+ *$', re.IGNORECASE)

stop_text = ' '
# This function reads the raw email message and creates a structured email class
def readEmail(msg):
    global stop_text
    from_=getmailaddresses(msg, 'from')
#    stop_text = stop_text  + ' | ' + getNames(msg, 'from')
#    stop_text = stop_text  + ' | ' + getNames(msg, 'to')
#    stop_text = stop_text  + ' | ' + getNames(msg, 'Cc')
#    stop_text = stop_text  + ' | ' + ' | '.join(getmailaddresses(msg, 'from'))
#    stop_text = stop_text  + ' | ' + ' | '.join(getmailaddresses(msg, 'to'))
#    stop_text = stop_text  + ' | ' + ' | '.join(getmailaddresses(msg, 'Cc'))
    f = ('') if not from_ else from_[0]
    _to = str(msg['To'])
    to_list = getmailaddresses(msg, 'to')
    #pre processing body
    attachments=get_mail_contents(msg)
    te =' '
    for attach in attachments:
        # for filename collision, to before to save :
        if attach.is_body=='text/plain':
            payload, used_charset=decode_text(attach.payload, attach.charset, 'auto')
            te = payload
        if attach.is_body=='text/html':
            payload, used_charset=decode_text(attach.payload, attach.charset, 'auto')
            te = payload
            te = h.handle(te) # To get the text from the HTML file
    te = re.sub(r'\* \* \*', "________________________________", te)    
    te = te.encode('ascii', 'ignore')
    subject = getmailheader(msg.get('Subject', ''))
    subject = re_fw_pattern.sub('', subject)
    subject = subject.encode('ascii', 'ignore')
    z = quotequail.unwrap(te) # To remove the reply text
    if z is not None:
        if 'text_top' in z:
            te = z["text_top"]
    te = regex_1.sub(' ',te)
    #pre processing subject
    cc = getmailaddresses(msg, 'Cc')
    if cc is not None:
        to_list = to_list + cc
    dt = getDateTime_numpy(str(msg['Date']))
    #dt = str(msg['Date'])
    e = Email(f, to_list,subject,te,dt)
    return e

def retrieveEmails_Enron(person, em_id):
    emails =set()
    directory = "/home/mallend1/Downloads/enron_mail/maildir/"+ person
    for root, dirs, file_names in os.walk(directory):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            message_file = file(file_path, "r")
            message_text = message_file.read()
            message_file.close()
            msg = email.message_from_string(message_text)
            f = str(msg['From'])
            if f=='None':
                continue
            _to = str(msg['To'])  
            if _to=='None':
                continue
            e = readEmail(msg)
            emails.add(e)
            #print e._from
            #print e.to_list
    return getCurrentUser(emails, em_id, person)

def retrieveEmails(conn, em_id , since_date, before_date):
    start=datetime.now()
    folders = conn.list()
    n = len(folders[1])
    emails =set()
    # iterates over all the folders
    print 'Reading Emails'
    for  i in range(1,n):
        folder = folders[1][i].split("\"")[3] # getting the names of the folders which are separated by quotes
        status = conn.select(folder, readonly=True)
        if(status[0]=='NO'):
            continue
        #result, data = conn.search(None, "ALL")
        try:
            result, data = conn.search( None, '((SINCE {since_date}) (BEFORE {before_date}))'.format(since_date = since_date, before_date = before_date))
        except Exception as e:
            print 'Bad Email'
            continue
        ids = data[0] # data is a list.
        print folder
        
        id_list = ids.split() # ids are a space separated string
        # iterates over all the mails
        print 'No of Emails:', len(id_list)
        no = 0
        for j in data[0].split():
            no= no+1
            new =  []
            try:
                typ, msg_data = conn.fetch(str(j), '(RFC822)')
            except Exception as e:
                print 'Bad Email'
                continue
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    if (msg['From'] == None):
                        continue
                    #print 'From:', str(msg['From'])
                    try:
                        e = readEmail(msg)
                        emails.add(e)
                    except Exception as e:
                        print 'Bad Email'
                        continue
            if(no%100 ==0):
                print 'Read '+ str(no) + ' Emails'+'.'*(no/100)
        print 'Total number of Extracted Emails:', len(emails)
    print 'Read All Emails'
    print 'Time taken to read all emails: ', datetime.now()-start
    return getCurrentUser(emails, em_id, ' ')


def getCurrentUser(emails, em_id, per):
    name_dict = {}
    try:
        with open('name_dictionary.txt') as f:
            content = f.readlines()
        for lin in content:
            lin = lin.replace('\n','')
            if(lin.split(':') ==[' ']):
                continue
            key,value = lin.split(':')
            name_dict[key] = value
    except Exception as e:
        print 'No file found'
    emails = list(emails)
    emails_list = []
    i=0
    people = set()
    # unlists the "to_list" and creates a one-to-one relation between from member and to member
    for em in emails:
        for _to in em.to_list:
            e = []
            e.append(i)
            f= em._from
            if (f in name_dict):
                f = name_dict[f]
            e.append(f)
            t = _to
            if (t in name_dict):
                t = name_dict[t]
            people.add(t)
            people.add(f)
            e.append(t)
            e.append(em._subject)
            e.append(em.date)
            emails_list.append(e)
        i=i+1
    print 'No of Emails with one to one relation between user and peer:', i
    return buildClassStructure(emails, emails_list, em_id, people)
    
def buildClassStructure(emails, emails_list, em_id, people):
    # identifies unique people interacted with
    #global stop_text 
    start=datetime.now()
    text_file = open("skills.txt", "r")
    lines = text_file.readlines()
    skill_set = set(lines)
    skill_set = set([element.lower().replace('\n','' ) for element in skill_set])
    tagger = ner.SocketNER(host='localhost', port=8080)
    unique_peeps = OrderedDict.fromkeys(people).keys()
    try:
        unique_peeps.remove(em_id)
    except Exception as e:
        print "Error with Email Id"
        print e
    print 'No of unique peers:', len(unique_peeps)
    # creates a Pandas Dataframe object
    df = pandas.DataFrame(emails_list, columns=['idd','_From', '_To', 'Subject', 'Date'])
    current_user = user(em_id)
    df.ix[1]
    df['Date'] = df['Date'].astype('datetime64[ns]')
    print 'Email ID:', current_user.email
    # For each person identify the unique subjects and store the list of email ids associated with the same subject
    for person in unique_peeps:
        no = 0
        #person = 'mark.elliott@enron.com'
        #q = "SELECT idd,_From,_To,Subject FROM df where (_From='%s' OR _TO = '%s') AND (_From='%s' OR _TO = '%s');"%(person,person,em,em)
        q = """SELECT Distinct Subject FROM df where (_From='%s' OR _TO = '%s') AND (_From='%s' OR _TO = '%s');"""%(person,person,em_id,em_id)
        #q = "SELECT idd,_From,_To,Subject FROM df where _From='%s' OR _TO = '%s';"%(person,person)
        #print locals()
        unique_subjects= sqldf(q, locals())
        if unique_subjects is not None:
            if unique_subjects.empty:
                continue
            inter = peer(person)
            peer_doc = []
            for i in range(0, len(unique_subjects.index)):
                sub = unique_subjects.ix[i].Subject
                id_list=[]
                q_1  = """SELECT idd,_from,_to,Date FROM df where (_From='%s' OR _TO = '%s') AND (_From='%s' OR _TO = '%s') AND Subject = "%s"  Order by Date; """%(person,person,em_id,em_id,sub)
                #print locals()
                ids = None
                try:
                    ids =  sqldf(q_1, locals())
                except Exception as e:
                    print 'Something wrong with mail from:',person
                    print e
                    continue
                #ids = df[((df._From == person) | (df._To == person)) & ((df._From == em_id) | (df._To == em_id)) & (df.Subject == str(sub))  ]
                mail_list_peer = []
                phrase_list_peer = []
                mail_list_user = []
                phrase_list_user = []
                people_list = []
                organization_list = [] 
                location_list = [] 
                doc_len_user = []
                doc_len_peer = []
                if ids is not None:
                    thd = thread(sub)
                    temp = getThreadLevelTemporal(ids, em_id, sub)
                    thd.initiator = temp['initiator']
                    thd.no_user = temp['No_messages_user']
                    thd.no_peer = temp['No_messages_peer']
                    thd.user_response_times = temp['user_response_times']
                    thd.peer_response_times = temp['peer_response_times']
                    for j in range(0, len(ids.index)):
                        id_list.append(ids.ix[j].idd.astype(int))
                        t = emails[ids.ix[j].idd.astype(int)]._body
                        p = zp.parse(t) 
                        body = p['body'] 
                        l = len(body)
                        try:
                            phrases = getPhrases(body, '')
                            phrases = phrases + list(tb(sub).noun_phrases)
                            NER = tagger.get_entities(body)
                            if('PERSON' in NER):
                                people_list = people_list + NER['PERSON']
                            if('ORGANIZATION' in NER):
                                organization_list = organization_list + NER['ORGANIZATION']
                            if('LOCATION' in NER):
                                location_list = location_list + NER['LOCATION']
                            if(ids.ix[j]._From == em_id):
                                #mail_list_user.append(preProcess(emails[ids.ix[j].idd.astype(int)]._body))
                                phrase_list_user = phrase_list_user+phrases
                                doc_len_user.append(l)
                                #print tb(p['body']).noun_phrases
                            else:
                                #mail_list_peer.append(preProcess(emails[ids.ix[j].idd.astype(int)]._body))
                                phrase_list_peer = phrase_list_peer+phrases
                                doc_len_peer.append(l)
                            #thd.document_user = ' '.join(mail_list_user)
                            #thd.document_peer = ' '.join(mail_list_peer)
                            thd.phrase_user = phrase_list_user
                            thd.phrase_peer = phrase_list_peer
                            thd.doc_length_user = doc_len_user
                            thd.doc_length_peer = doc_len_peer
                            sk = phrase_list_user + phrase_list_peer
                            sk = [element.lower().replace('\n','' ) for element in sk]
                            thd.skills = list(skill_set.intersection(sk))
                            thd.email_list = list(id_list)
                            thd.people = people_list
                            thd.organizations = organization_list
                            thd.locations = location_list
                        except Exception as e:
                            print 'Something wrong with mail from:',person
                            print e
                    inter.thread_list.append(thd)
            current_user.peer_list.append(inter)
    print 'BUILT USER CLASS'
    print 'Time taken to build class structure:', datetime.now()-start
    return current_user
    #
#    ##Prints the No. of Emails Exchanged and the subject of the thread which has maximum emails associated with each peer
#    print(len(current_user.peer_list))
#    for inter in current_user.peer_list:
#        print inter.email
#        print "No of Threads:", len(inter.thread_list)
#        print "No of Emails Exchanged",  getTotalEmails(inter)
#        m =  max(inter.thread_list, key = byEmailNo)
#        print "Thread with maximum emails:", m.subject
#        print "length:", len(m.email_list)
#        print '\n'


def getOrganizations(current_user):
    ret = []
    for inter in current_user.peer_list:
        t = inter.getOrganizations()
        if( len(t) == 0 ):
            continue
        #print inter.email
        #print set(t)
        ret = ret+t
    return set(ret)

def getLocations(current_user):
    ret = []
    for inter in current_user.peer_list:
        t = inter.getLocations()
        if( len(t) == 0 ):
            continue
        #print inter.email
        #print set(t)
        ret = ret+t
    return set(ret)
        
def getPeople(current_user):
    ret = []
    for inter in current_user.peer_list:
        t = inter.getPeople()
        if( len(t) == 0 ):
            continue
        #print inter.email
        #print set(t)
        ret = ret+t
    return set(ret)
    
def getSkills(current_user):
    ret = []
    for inter in current_user.peer_list:
        t = inter.getSkills()
        if(len(t) == 0 ):
            continue
        #print inter.email
        #print set(t)
        ret = ret+t
    return set(ret)

def getTimeLengthStats(current_user):
    for inter in current_user.peer_list:
        if(inter.getAVGUserResponseTimes()  == 0 and inter.getAVGPeerResponseTimes() ==0 ):
            continue
        print inter.email
        print "Total No of Emails Exchanged",  getTotalEmails(inter)
        print "User Median", inter.getMedianUserResponseTimes()
        print "User Average", inter.getAVGUserResponseTimes() 
        print "Peer Median", inter.getMedianPeerResponseTimes()
        print "Peer Average", inter.getAVGPeerResponseTimes()
        print "Text Length User Median", inter.getMedianUserTextLength()
        print "Text Length User Average", inter.getMeanUserTextLength() 
        print "Text Length Peer Median", inter.getMedianPeerTextLength()
        print "Text Length Peer Average", inter.getMeanPeerTextLength()
        print "Initiation Probabilities", inter.getInitiationProbabilities()
    
def getTopWords(current_user, level, p, doc_list_flag, i_peer_list):
    #usage: getTopWords(current_user,'peer','both',True)
    # doc_list_flag indicates whether the list must be initialised just once or must be initialised for every peer
    # doc_list_flag = True then doc_list is initialised for every peer.
    if (level =='peer'):
        doc_list = []
        for inter in current_user.peer_list:
            doc_list.append(TextBlob(inter.getDocument(p)))
        for inter in current_user.peer_list:
            if(inter.email not in i_peer_list):
                continue
            print inter.email
            print getTopWordsTFIDF(TextBlob(inter.getDocument(p)),doc_list,5)
            print '\n'
    elif (level =='thread'):
        doc_list = [] 
        if(doc_list_flag):
            for inter in current_user.peer_list:
                doc_list= []
                if(inter.email not in i_peer_list):
                    continue
                print inter.email
                for thread in inter.thread_list:
                    doc_list.append(TextBlob(thread.getDocument(p)))
                for thread in inter.thread_list:
                    print thread.subject, len(thread.email_list)
                    print getTopWordsTFIDF(TextBlob(thread.getDocument(p)),doc_list,5)
                    print '\n'
        else:
            doc_list= []
            for inter in current_user.peer_list:
                for thread in inter.thread_list:
                    doc_list.append(TextBlob(thread.getDocument(p)))
            for inter in current_user.peer_list:
                if(inter.email not in i_peer_list):
                    continue
                for thread in inter.thread_list:
                    print thread.subject, len(thread.email_list)
                    print getTopWordsTFIDF(TextBlob(thread.getDocument(p)),doc_list,5)
                    print '\n'

def getTopSkills(current_user, k):
    doc_list = []
    skills = []
    for inter in current_user.peer_list:
        skills = skills +inter.getSkills()
        doc_list.append(inter.getSkills())
    blob = skills
    bloblist = doc_list
    scores = {word: (tf(word, blob)*n_containing(word, bloblist)) for word in blob}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    topWords = []
    for word, score in sorted_words[:k]:
        new = []
        new.append(word)
        new.append(round(score, 5))
        topWords.append(new)
    return topWords
    

def getTopSkillsHierarchy(current_user):
    skills = []
    for inter in current_user.peer_list:
        skills = skills +inter.getSkills()
    skills = set(skills)
    lis = []
    for sk in skills:
        lis = lis + getAncestors(sk)
    scores = {word: (tf(word, lis)) for word in lis}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print sorted_words

def getAllStats(current_user,peer_list, file ):
    for inter in current_user.peer_list:
        if(inter.email not in peer_list):
            continue
        file.write('\n')
        file.write('\n')
        file.write('\n'+'  '+str(inter.email))
        file.write('\nSkills:' +'  '+str(set(inter.getSkills())))
        file.write('\nTop 10 Skills:' +'  '+str(getTopSkills(current_user, 10)))
        file.write('\nPeople:' +'  '+str(set(inter.getPeople())))
        file.write('\nLocations:' +'  '+str(set(inter.getLocations())))
        file.write('\nOrganizations:' +'  '+str(set(inter.getOrganizations())))
        file.write( "\nTotal No of Emails Exchanged" +'  '+str(getTotalEmails(inter)))
        file.write("\nUser Median" +'  '+str(inter.getMedianUserResponseTimes()))
        file.write("\nUser Average" +'  '+str(inter.getAVGUserResponseTimes() ))
        file.write("\nPeer Median" +'  '+str( inter.getMedianPeerResponseTimes()))
        file.write("\nPeer Average" +'  '+str( inter.getAVGPeerResponseTimes()))
        file.write("\nText Length User Median"+'  '+str(inter.getMedianUserTextLength()))
        file.write("\nText Length User Average" +'  '+str( inter.getMeanUserTextLength() ))
        file.write("\nText Length Peer Median" +'  '+str( inter.getMedianPeerTextLength()))
        file.write("\nText Length Peer Average" +'  '+str( inter.getMeanPeerTextLength()))
        file.write("\nInitiation Probabilities" +'  '+str(inter.getInitiationProbabilities()))

def getAllStats_DF(current_user):
    df = pandas.DataFrame(columns = ['name','times', 'Threads','No of emails', 'Text Length'])
    i = 0
    for inter in current_user.peer_list:
        if (inter.getMedianUserResponseTimes() == 0):
            continue
        df.loc[i] = [inter.email, inter.getMedianUserResponseTimes(),byThreadNo(inter),  getTotalEmails(inter),  inter.getMedianUserTextLength() ]
        i = i+1
    df = df.sort('times')
    df.index = range(len(df))
    return df
