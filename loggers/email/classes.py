from dateUtils import *
class user(object):
    def __init__(self, email):
        self.email=email
        self.peer_list = []

class peer(object):
    def __init__(self, email):
        self.email = email
        self.thread_list=[]

    def getDocument(self, p):
        if(p == 'user'):
            lis = []
            for thd in self.thread_list:
                lis.append(thd.document_user)
            return  ' '.join(lis)
        elif(p=='peer'):
            lis = []
            for thd in self.thread_list:
                lis.append(thd.document_peer)
            return  ' '.join(lis)
        else:
            lis = []
            for thd in self.thread_list:
                lis.append(thd.document_user)
                lis.append(thd.document_peer)
            return  ' '.join(lis)
    
    def getPhrase(self, p):
        if(p == 'user'):
            lis = []
            for thd in self.thread_list:
                lis = lis + thd.phrase_user
            return  lis
        elif(p=='peer'):
            lis = []
            for thd in self.thread_list:
                lis= lis + thd.phrase_peer
            return lis
        else:
            lis = []
            for thd in self.thread_list:
                lis= lis +thd.phrase_user
                lis= lis +thd.phrase_peer
            return  lis
    
    def getSkills(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.skills
        return lis
        
    def getOrganizations(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.organizations
        return lis

    def getLocations(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.locations
        return lis

    def getPeople(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.people
        return lis
    
    def getMedianUserResponseTimes(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.user_response_times
        return getMedianTime(lis)
        
    def getMedianPeerResponseTimes(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.peer_response_times
        return getMedianTime(lis)
    
    def getAVGUserResponseTimes(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.user_response_times
        return getMeanTime(lis)

    def getAVGPeerResponseTimes(self):
        lis = []
        for thd in self.thread_list:
            lis = lis + thd.peer_response_times
        return getMeanTime(lis)
    
    def getInitiationProbabilities(self):
        n = len(self.thread_list)
        p_count = 0
        for thd in self.thread_list:
            if(thd.initiator == self.email ):
                p_count = p_count+1
        
        ret = {
        'peer': p_count/ float(n), 
        'user': 1 - (p_count/float(n))
        }
        return ret

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
        self.document_user = " "
        self.document_peer = " "
        self.phrase_user = []
        self.phrase_peer = []
        self.email_list=[]
        self.initiator = ''
        self.no_user = 0
        self.no_peer = 0
        self.user_response_times = []
        self.peer_response_times = []
        self.people = []
        self.organizations = []
        self.locations = []
        self.skills = [] 
    def getDocument(self,p):
        if(p == 'user'):
            return self.document_user
        elif(p=='peer'):
            return self.document_peer
        else:
            return self.document_user+ ' ' + self.document_peer
    def getPhrase(self,p):
        if(p == 'user'):
            return self.phrase_user
        elif(p=='peer'):
            return self.phrase_peer
        else:
            return self.phrase_user+self.phrase_peer

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

