import imaplib
import email
emails = []
conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
EMAIL = '<gmail-id>'
PASSWORD = '<password>'
conn.login(EMAIL, PASSWORD)
for folder in ['[Gmail]/Sent Mail','INBOX']:
    conn.select(folder, readonly=True)
    result, data = conn.search(None, "ALL")
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string
    latest_email_id = id_list[-1] # get the latest
    for i in range(1,int(latest_email_id)):
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
