#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import xmlrpclib
import sys

def print_help():
	print "Usage:"
	print "\tpython stdin.py target message[ password]"
	print "\tpython stdin.py target[ password]\t\t<<< standard input"

###

sys.argv.pop(0)
argc = len(sys.argv)

if argc == 0:
	print_help()
	sys.exit()

target = sys.argv[0]
password = None
message = None
	
if argc == 2:
	password = sys.argv[1]
	
if argc >= 3:
	message = sys.argv[1]
	password = sys.argv[2]

###

client = xmlrpclib.ServerProxy("http://localhost:8000", allow_none = True)

if not message:
	message = sys.stdin.read()

client.ircgate(target, message, password)

