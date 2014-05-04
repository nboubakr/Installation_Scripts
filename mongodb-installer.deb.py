#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# mongodb-installer.deb.py
# Simple python script to install MongoDB on Debian/Ubuntu
#
# Boubakr NOUR <n.boubakr@gmail.com>
#
# Thanks to: Nicolargo (aka) Nicolas Hennion
#
# TODO List
# Checks the internet conenctivity beofre start the installation


import os
import sys
import platform
import getopt
import shutil
import logging
import getpass


_VERSION="0.1"
_DEBUG = 0


class colors:
	RED = '\033[91m'
	GREEN = '\033[92m'
	BLUE = '\033[94m'
	ORANGE = '\033[93m'
	NO = '\033[0m'

	def disable(self):
		self.RED = ''
		self.GREEN = ''
		self.BLUE = ''
		self.ORANGE = ''
		self.NO = ''


def init():
	# Globals variables
	global _VERSION
	global _DEBUG

	# Set the log configuration
	logging.basicConfig(
		filename = '/tmp/mongodb_installer.deb.log',
		level = logging.DEBUG,
		format = '%(asctime)s %(levelname)s - %(message)s',
	 	datefmt = '%d/%m/%Y %H:%M:%S',
	)

def syntax():
	print "Run the script as root:"
	print "sudo python mongodb-installer.deb.py"
	print
	print "-h\tGet this message"
	print "-v\tGet the script version"
	print "-d\tRun the script on debug mode"
	print


def version():
	sys.stdout.write ("MongoDB Installer version %s" % _VERSION)
	sys.stdout.write (" (running on %s %s)\n" % (platform.system() , platform.machine()))


def showexec(description, command, exitonerror = 0):
	"""
	Exec a system command with a pretty status display (Running / Ok / Warning / Error)
	By default (exitcode=0), the function did not exit if the command failed
	"""

	if _DEBUG: 
		logging.debug ("%s" % description)
		logging.debug ("%s" % command)

	# Manage very long description
	if (len(description) > 65):
		description = description[0:65] + "..."
		
	# Display the command
	status = "[Running]"
	statuscolor = colors.BLUE
	sys.stdout.write (colors.NO + "%s" % description + statuscolor + "%s" % status.rjust(79-len(description)) + colors.NO)
	sys.stdout.flush()

	# Run the command
	returncode = os.system ("/bin/sh -c \"%s\" >> /dev/null 2>&1" % command)
	
	# Display the result
	if returncode == 0:
		status = "[  OK   ]"
		statuscolor = colors.GREEN
	else:
		if exitonerror == 0:
			status = "[Warning]"
			statuscolor = colors.ORANGE
		else:
			status = "[ Error ]"
			statuscolor = colors.RED

	sys.stdout.write (colors.NO + "\r%s" % description + statuscolor + "%s\n" % status.rjust(79-len(description)) + colors.NO)

	if _DEBUG: 
		logging.debug ("Returncode = %d" % returncode)

	# Stop the program if returncode and exitonerror != 0
	if ((returncode != 0) & (exitonerror != 0)):
		if _DEBUG: 
			logging.debug ("Forced to quit")
		exit(exitonerror)

def getpassword(description = ""):
	"""
	Read password (with confirmation)
	"""
	if (description != ""): 
		sys.stdout.write ("%s\n" % description)
		
	password1 = getpass.getpass("Password: ");
	password2 = getpass.getpass("Password (confirm): ");

	if (password1 == password2):
		return password1
	else:
		sys.stdout.write (colors.ORANGE + "[Warning] Password did not match, please try again" + colors.NO + "\n")
		return getpassword()
		
def main(argv):
	logging.info("Start")
	# logging.warning("Warning")
	# logging.debug("Debug")
	# logging.info("End")

	try:
		opts, args = getopt.getopt(argv, "hvd", ["help", "version", "debug"])
	except getopt.GetoptError:
		syntax()
		exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			syntax()
			exit()
		elif opt == '-v':
			version()
			exit()
		elif opt == '-d':
			global _DEBUG
			_DEBUG = 1

	# pw = getpassword ("Enter a dummy password...")
	showexec("Import the public key used by the package management system", "apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10")
	showexec("Create the source list file for MongoDB", "echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' > /etc/apt/sources.list.d/mongodb.list")
	showexec("Reload local package database", "apt-get update")
	showexec("Install the MongoDB packages", "apt-get install mongodb-org")
	showexec("Start MongoDB", "/etc/init.d/mongod start")
	

if __name__ == "__main__":
	
	sys.stdout.write ("\n\tMongoDB installation script for Debian/Ubuntu\n\n")

	# Checks if the user is root !
	if not os.geteuid() == 0:
		sys.exit("\nThis script must be run as root...\n")

	init()
	main(sys.argv[1:])

	print "\nCleaning up..."
	exit()

# EOF