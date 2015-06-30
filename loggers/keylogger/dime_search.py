#!/usr/bin/python
# -*- coding: utf-8 -*-

# For DiMe server queries
import requests
import socket
import json


################################################################


def search_dime(username, password, query):
	#------------------------------------------------------------------------------

	server_url = 'http://localhost:8080/api'
	server_username = str(username)
	server_password = str(password)

	#------------------------------------------------------------------------------

	# ping server (not needed, but fun to do :-)
	r = requests.post(server_url + '/ping')

	if r.status_code != requests.codes.ok:
	    print('No connection to DiMe server!')
	    sys.exit(1)

	# make search query
	#query = "dime"
	#query = "python"

	r = requests.get(server_url + '/search?query={}&limit=5'.format(query),
        	         headers={'content-type': 'application/json'},
                	 auth=(server_username, server_password),
	                 timeout=10)
	
	print query
	print len(r.json())

	if len(r.json()) > 0:
		if r.status_code != requests.codes.ok:
		    #print('ErrorNo connection to DiMe server!')
		    r = None
		    #sys.exit(1)

		return r

