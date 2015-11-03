import email
import imaplib
import getpass
import string
from textblob import TextBlob as tb
import sys
import quotequail
import re
from bs4 import BeautifulSoup
import html2text
h = html2text.HTML2Text()
h.ignore_links = True
class Email(object):
	def __init__(self):
        	self.message_id = ''
		self.from_ = ''
	        self.to_list = []
		self.tags = []
        	self.subject = ''
	        self.body = ''
        	self.date = ''
		self.attachments = []
        def to_JSON(self):
        	return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4) 
	
def getPhrases(text):
    text = re.sub(u"(\u2018|\u2019)", " ", text)
    np = tb(text).noun_phrases
    ret = []
    for t in np:
        temp = ' '.join([word for word,pos in tb(t).tags if pos in ('NNP','NNS','NN','NNPS') and word not in set(string.punctuation)])
        #temp = t
        if (temp not in(' ', '')):
            ret.append(temp)
    return ret		
	
def readEmails(msg):
	em = Email()
	em.message_id = msg['Message-id']
	em.from_ = msg['From']
	if(msg['To'] is not None):
		em.to_list = em.to_list + msg['To'].split(',')
	if(msg['Cc'] is not None):
		em.to_list = em.to_list + msg['Cc'].split(',')
	em.subject = msg['Subject']
	maintype = msg.get_content_maintype()
    	if maintype == 'text':
		charset = msg.get_content_charset()
        	em.body = em.body + msg.get_payload(decode=True)
	attachments = []
	for part in msg.walk():
		if part.get_content_maintype() == 'multipart':
	            for p in part.get_payload():
			if p.get_content_maintype() == 'text':
			    charset = p.get_content_charset()
		            em.body = em.body + p.get_payload(decode=True)
		    continue
		if part.get('Content-Disposition') is None:
		    continue
            	attach = {}
	        attach['filename'] = part.get_filename()
	        attach['content'] = part.get_payload(decode=True)
	        attachments.append(attach)
	#print em._body
	em.body = em.body.decode('ascii','ignore')
	#print em._body

	if(bool(BeautifulSoup(em.body, "html.parser").find())):
		em.body  = h.handle(em.body) 
	z = quotequail.unwrap(em.body)
	if z is not None:
        	if 'text_top' in z:
	            em.body = z["text_top"]
	#print em._body
	em.attachments = attachments
	em.tags = list(set(getPhrases(em.body)))
	return em

if __name__ == "__main__":
	emails = []
	if(len(sys.argv) > 1):
        #domain = 'imap.aalto.fi'
        	domain = sys.argv[1]
	        conn = imaplib.IMAP4_SSL(domain, 993)
        	USERNAME =  sys.argv[2]
	        print USERNAME
	        #em_id =  sys.argv[3]
        	#print em_id
        	PASSWORD =  getpass.getpass("Enter your Password:")
	        conn.login(USERNAME, PASSWORD)
        	since_date = sys.argv[3]
	        if( since_date == ''):
        	    since_date = '01-JUN-2015'
	        before_date = sys.argv[4]
        	if( before_date == ''):
	            before_date = '28-JUL-2015'
		rv,folders = conn.list()
		n = len(folders)
		for  i in range(1,n):
			sp = folders[i].split("\"") # getting the names of the folders which are separated by quotes
			if(len(sp) == 5):
				folder = sp[3]
			elif(len(sp) == 3):
				folder = sp[2].replace(' ','')
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
				try:
					typ, msg_data = conn.fetch(str(j), '(RFC822)')
				except Exception as e:
					print 'Bad Email'
					continue
				for response_part in msg_data:
					if isinstance(response_part, tuple):
						msg = email.message_from_string(response_part[1])
						emails.append(readEmails(msg))                    
				if(no%100 ==0):
					print 'Read '+ str(no) + ' Emails'+'.'*(no/100)
			print 'Total number of Extracted Emails:', len(emails)
		#conn.close()
		conn.logout()
	        print 'Read All Emails'

