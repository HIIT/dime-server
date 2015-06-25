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
from nltk.corpus import stopwords
import imaplib
import email
import keyring
from textUtils import *
from parseMail import *
from textblob import TextBlob as tb
import html2text
import quotequail
 
#conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
# Log In
conn = imaplib.IMAP4_SSL("imap.aalto.fi", 993)
USERNAME = 'mallend1'
email_id = 'darshan.mallenahallishankaralingappa@aalto.fi' #user-id
em_id = email_id
PASSWORD = keyring.get_password('my_Gmail',USERNAME)
conn.login(USERNAME, PASSWORD)
folders = conn.list()
n = len(folders[1])
h = html2text.HTML2Text()
h.ignore_links = True
# Regex patterns to remove to escape sequences and other characters from the email-id
regex = re.compile(r'[ \n\r\t\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]')
regex_1 = re.compile(r'[\n\r\t\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]')
re_fw_pattern =re.compile( '([\[\(] *)?(RE|FWD?) *([-:;)\]][ :;\])-]*|$)|\]+ *$', re.IGNORECASE)

# Class User to analyse the person whose emails are to be analysed
# peer_list is the list of peers the user has interacted with
class user(object):
    def __init__(self, email):
        self.email=email
        self.peer_list = []

class peer(object):
    def __init__(self, email):
        self.email = email
        self.document = "document"
        self.thread_list=[]

def byThreadNo(inter):
    return len(inter.thread_list)

def byEmailNo(thread):
    return len(thread.email_list)


def getTotalEmails(inter):
    ret = 0
    for thrd in inter.thread_list:
        ret = ret+ len(thrd.email_list)
    return ret

# thread is used to represent the list of emails exchanged between the user and peer with the same subject
class thread(object):
    def __init__(self, subject):
        self.subject = subject
        self.document = "document"
        self.email_list=[]

#Emails class stores all the info regarding emails
# __repr__, __eq__ and __hash__ are over ridden to implement the set data structure
class Email(object):
    def __init__(self,_from, to_list, _subject, _body, date):
        self._from = _from
        self.to_list = to_list
        self._subject = _subject
        self._body = _body
        self.date = date
    def __repr__(self):
        return "(%s,%s,%s,%s,%s)" % (self._from, self.to_list, self._subject, self._body, self.date)
    def __eq__(self, other):
        if isinstance(other, Email):
            return (self.__repr__() == other.__repr__())
        else:
            return False
    def __hash__(self):
        return hash(self.__repr__())

		

# This function reads the raw email message and creates a structured email class
def readEmail(msg):
    from_=getmailaddresses(msg, 'from')
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
    z = quotequail.unwrap(te) # To remove the reply text
    if z is not None:
        if 'text_top' in z:
            te = z["text_top"]
    #print te
    te = regex_1.sub(' ',te)
    #pre processing subject
    #pre processing subject
    subject = getmailheader(msg.get('Subject', ''))
    subject = re_fw_pattern.sub('', subject)
    cc = getmailaddresses(msg, 'Cc')
    if cc is not None:
        to_list = to_list + cc
    e = Email(f, to_list,subject,te,str(msg['Date']))
    return e

emails =set()
print n
# iterates over all the folders
for  i in range(1,n):
    folder = folders[1][i].split("\"")[3] # getting the names of the folders which are separated by quotes
    status = conn.select(folder, readonly=True)
    if(status[0]=='NO'):
        continue
    result, data = conn.search(None, "ALL")
    ids = data[0] # data is a list.
    id_list = ids.split() # ids are a space separated string
    # iterates over all the mails
    for j in range(1,len(id_list)):
        new =  []
        typ, msg_data = conn.fetch(str(j), '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                e = readEmail(msg)
                emails.add(e)


emails = list(emails)
emails_list = []
i=0
people = []
# unlists the "to_list" and creates a one-to-one relation between from member and to member
for email in emails:
    for _to in email.to_list:
        e = []
        e.append(i)
        f= email._from
        if f=='None':
            print 'Yes'
        e.append(f)
        t = _to
        if t=='None':
            print 'Yes'
        people.append(t)
        e.append(t)
        e.append(email._subject)
        e.append(email.date)
        emails_list.append(e)
    i=i+1

# identifies unique people interacted with
unique_peeps = OrderedDict.fromkeys(people).keys()
unique_peeps.remove(em_id)
# creates a Pandas Dataframe object
df = pandas.DataFrame(emails_list, columns=['idd','_From', '_To', 'Subject', 'Date'])
current_user = user(em_id)
print(current_user.email)

# For each person identify the unique subjects and store the list of email ids associated with the same subject
for person in unique_peeps:
    no = 0
    #person = 'mark.elliott@enron.com'
    #q = "SELECT idd,_From,_To,Subject FROM df where (_From='%s' OR _TO = '%s') AND (_From='%s' OR _TO = '%s');"%(person,person,em,em)
    q = """SELECT Distinct Subject FROM df where (_From='%s' OR _TO = '%s') AND (_From='%s' OR _TO = '%s');"""%(person,person,em_id,em_id)
    #q = "SELECT idd,_From,_To,Subject FROM df where _From='%s' OR _TO = '%s';"%(person,person)
    unique_subjects= sqldf(q, globals())
    if unique_subjects.empty:
        continue
    inter = peer(person)
    peer_doc = []
    for i in range(0, len(unique_subjects.index)):
        sub = unique_subjects.ix[i].Subject
        thd = thread(sub)
        id_list=[]
        q_1  = """SELECT idd FROM df where (_From='%s' OR _TO = '%s') AND (_From='%s' OR _TO = '%s') AND Subject = "%s";"""%(person,person,em_id,em_id,str(sub.encode('ascii', 'ignore')))
        ids =  sqldf(q_1, globals())
        #ids = df[((df._From == person) | (df._To == person)) & ((df._From == em_id) | (df._To == em_id)) & (df.Subject == str(sub))  ]
        mail_list = []
        for j in range(0, len(ids.index)):
            id_list.append(ids.ix[j].idd.astype(int))
            mail_list.append(preProcess(emails[ids.ix[j].idd.astype(int)]._body))
        thd.document = ' '.join(mail_list)
        peer_doc.append(thd.document)
        thd.email_list = list(id_list)
        inter.thread_list.append(thd)
        #print sqldf(q_1, globals())
    inter.document = ' '.join(peer_doc)
    current_user.peer_list.append(inter)

#Prints the No. of Emails Exchanged and the subject of the thread which has maximum emails associated with each peer
print(len(current_user.peer_list))
for inter in current_user.peer_list:
    print inter.email
    print "No of Threads:", len(inter.thread_list)
    print "No of Emails Exchanged",  getTotalEmails(inter)
    m =  max(inter.thread_list, key = byEmailNo)
    print "Thread with maximum emails:", m.subject
    print "length:", len(m.email_list)
    print '\n'

print "Top Words"
def getTopWords(level):
    if (level =='peer'):
        doc_list = []
        for inter in current_user.peer_list:
            doc_list.append(tb(inter.document))
        for inter in current_user.peer_list:
            print inter.email
            print getTopWordsTFIDF(tb(inter.document),doc_list,3)
            print '\n'
    elif (level =='thread'):
        for inter in current_user.peer_list:
            print inter.email
            doc_list = []
            for thread in inter.thread_list:
                doc_list.append(tb(thread.document))
            for thread in inter.thread_list:
                print thread.subject
                print getTopWordsTFIDF(tb(thread.document),doc_list,5)
                print '\n'

getTopWords('thread')
