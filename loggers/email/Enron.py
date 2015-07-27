import email
from classes import *
from os import listdir, chdir
from retrieveEmails import *
from Topic_Modelling_Noun_Phrases import *

DIR = "/home/mallend1/Downloads/enron_mail/maildir"
chdir(DIR)
names = [d for d in listdir(".") if "." not in d]
emails = [] 
print names
for name in names:
    chdir(DIR+'/'+name)
    print name
    directory = "/home/mallend1/Downloads/enron_mail/maildir/"+ name
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
            emails.append(e)
    print"length", len(emails)

#emails = list(emails)
emails_list = []
i=0
people = set()
# unlists the "to_list" and creates a one-to-one relation between from member and to member
for em in emails:
    for _to in em.to_list:
        e = []
        e.append(i)
        f= em._from
        if f=='None':
            print 'Yes'
        e.append(f)
        t = _to
        if t=='None':
            print 'Yes'
        people.add(t)
        people.add(f)
        e.append(t)
        e.append(em._subject)
        e.append(em.date)
        emails_list.append(e)
    i=i+1
print i
