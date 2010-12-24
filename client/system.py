#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import xmlrpclib

client = xmlrpclib.ServerProxy("http://localhost:8000", allow_none = True)

client.shutdown("1234")
#client.reload("1234")
