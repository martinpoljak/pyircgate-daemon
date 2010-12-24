#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import SimpleXMLRPCServer

class XMLRPCRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler, object):
	
	def __init__(self, socket, address, server):
		super(XMLRPCRequestHandler, self).__init__(socket, address, server)
		self.server.source_instance = server.owner
		
class XMLRPCDispatcher(SimpleXMLRPCServer.SimpleXMLRPCDispatcher, object):
	source_instance = None

	def _dispatch(self, data, params):
		
		params = list(params)
		params.insert(0, self.owner)
		params = tuple(params)
		
		return super(XMLRPCDispatcher, self)._dispatch(data, params)

class XMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer, XMLRPCDispatcher, object):

	owner = None
	
	def __init__(self, addr, requestHandler = XMLRPCRequestHandler, logRequests = True, allow_none = False, encoding = None, source = None):
		self.owner = source
		super(XMLRPCServer, self).__init__(addr, requestHandler, logRequests, allow_none, encoding)
	
