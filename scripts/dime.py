#!/usr/bin/env python

# In order to run this script, the Python keyring library needs to be installed on the computer.


import keyring
import getpass

# hack to make raw_input work with both Python 2 and 3 :-)
try: input = raw_input
except NameError: pass

def new_password(username):
	print("Password for " + username + " not stored on this computer.")
	password = getpass.getpass("Enter password to be stored: ")
	keyring.set_password("DiMe", username, password)
	return password

# def existing_password(username):
#	testi = getpass.getpass("Enter password for " + username + ": ")

#	while testi != keyring.get_password("DiMe", username):
#		testi = getpass.getpass("Incorrect password, try again: ")
#		#jos haluaa luovuttaa niin mit sit?
#	print("Correct password.")
#	return True

def password(username=None):
	if username is None:
		username = input("Enter username: ")

	existing_password = keyring.get_password("DiMe", username)
	if existing_password is not None:
		return existing_password
	else:
		return new_password(username)





