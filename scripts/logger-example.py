#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

#------------------------------------------------------------------------------

r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))

# Set all the standard event fields
payload = {
    '@type':    'SearchEvent',
    'actor':    'logger-example.py',
    'origin':   socket.gethostbyaddr(socket.gethostname())[0],
    'type':     'http://www.hiit.fi/ontologies/dime/#ExampleSearchEvent',
    'start':    time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    'duration': 0,
    'query': 'cats',
    'tags': [
        { '@type': 'Tag', 
          'text': 'tag1', 
          'auto': False, 
          'actor': 'logger-example.py',
      },
        { '@type': 'Tag', 
          'text': 'tag2', 
          'auto': False,
          'weight': 0.1
      }
    ]
}

# payload = {
#     # this corresponds to the Java event class
#     "@type": "DesktopEvent",
#     # the program that produced the event, here the web browser
#     "actor": "DiMe browser extension",   
#     # time stamp when the event was started
#     "start": "2015-08-11T12:56:53Z", 
#     # type using the Semantic Desktop ontology
#     "type": 'http://www.semanticdesktop.org/ontologies/2010/01/25/nuao/#UsageEvent',
#     "targettedResource": {
#         "@type": "WebDocument",
#         # title of the Web page
#         "title": "Join, or Die - Wikipedia, the free encyclopedia", 
#         # type using the Semantic Desktop ontology
#         "isStoredAs": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#RemoteDataObject",
#         # the plain text in the webpage
#         "plainTextContent": "From Wikipedia, the free encyclopedia....",
#         "mimeType": "text/html",
#         # the URI of the web page or document
#         "uri": "https://en.wikipedia.org/wiki/Join,_or_Die",
#         "type": 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#HtmlDocument',
#         #a list of 8 tags defined by Tag class, the 8 tags are the most frequent terms on the page
#         "tags": [{"@type": "Tag", "text": "wikipedia"}],
#         #a list of terms in the webpage, ranked by frequency
#         "frequentTerms": ["wikipedia", "hurrican"],
#         #abstract/excerpt of the page
#         "abstract": '',
#         #a string of plain HTML with class/id/styles removed  
#         "HTML": "<p>From Wikipedia, the free encyclopedia</p> ...",
#         #a list of imgages in the page
#         "imgURLs": [{'url':'http://.../a.jpg', 'text': 'a pic'}],
#         #a list of hyperlinks in the page
#         "hyperLinks": [{'url': 'http://.../', 'text': 'a link'}],
#         #a list of Open Graph protocol http://ogp.me/
#         "OpenGraphProtocol": {
#             "image": "https://www.facebook.com/images/fb_icon_325x325.png",
#             "url": "https://www.facebook.com/",
#             "site_name": "Facebook",
#             "locale": "en_US"
#         },
#         #a list of HTML meta tags http://www.w3schools.com/tags/tag_meta.asp
#         "MetaTags": [{'name': 'description', 'content': 'Free Web tutorials'}],
#     },
# }

r = requests.post(server_url + '/data/event',
                  data=json.dumps(payload),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

print('DiMe returns:', json.dumps(r.json(), indent=2))
