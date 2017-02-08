#!/usr/bin/env python

# In order to run this script, the Python keyring library needs to be installed on the computer.


import keyring
import getpass

def new_password(username):
	password = getpass.getpass("Enter password for " + username + ": ")
	keyring.set_password("DiMe", username, password)


def existing_password(username):
	
	testi = getpass.getpass("Enter password for " + username + ": ")

	while testi != keyring.get_password("DiMe", username):
		testi = getpass.getpass("Incorrect password, try again: ")
		#jos haluaa luovuttaa niin mit sit?
	print("Correct password.")
	return True

def password():
	username = raw_input("Enter username: ")

	if keyring.get_password("DiMe", username) is not None:
		existing_password(username)
	else:
		answer = raw_input("Password for " + username + " not stored on this computer. Store a new password? (y/n) ")
		if answer == "y":
			new_password(username)
		else:
			password()

	#print keyring.get_password("DiMe", username)





