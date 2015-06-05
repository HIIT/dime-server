import imaplib
import email
emails = []
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
EMAIL = '<email-id>'
PASSWORD = '<password>'
conn.login(EMAIL, PASSWORD)
folders = conn.list()
n = len(folders[1])
for  i in range(1, n):
    folder = folders[1][i].split("\"")[3] # getting the names of the folders which are separated by quotes
    status = conn.select(folder, readonly=True)
    if(status[0]=='NO'):
        continue
    result, data = conn.search(None, "ALL")
    ids = data[0] # data is a list.
    id_list = ids.split() # ids are a space separated string
    print len(id_list)
    for i in range(1,len(id_list)):
        print i
        new =  []
        typ, msg_data = conn.fetch(str(i), '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
            	msg = email.message_from_string(response_part[1])
            	for header in ['to', 'from' ]:
		    new.append(msg[header])
		    print '%-8s: %s' % (header.upper(), msg[header])
	emails.append(new)
# To save the emails into a file
import pickle
pickle.dump(emails, open( "save.p", "wb" ) )
emails = pickle.load( open( "save.p", "rb" ) )

