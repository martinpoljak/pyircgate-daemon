#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import xmlrpclib

client = xmlrpclib.ServerProxy("http://localhost:8000", allow_none = True)
client.ircgate("first", "abc", "1234")
