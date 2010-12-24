#! /usr/bin/python
# -*- coding: utf-8 -*-
#

from libraries import SimpleJSONRPCServer

class JSONRPCRequestHandler(SimpleJSONRPCServer.SimpleJSONRPCRequestHandler, object):
	
	def __init__(self, socket, address, server):
		super(JSONRPCRequestHandler, self).__init__(socket, address, server)
		self.server.source_instance = server.owner
		
class JSONRPCDispatcher(SimpleJSONRPCServer.SimpleJSONRPCDispatcher, object):
	source_instance = None

	def _dispatch(self, data, params):
		
		params = list(params)
		params.insert(0, self.owner)
		params = tuple(params)
		
		return super(JSONRPCDispatcher, self)._dispatch(data, params)

class JSONRPCServer(SimpleJSONRPCServer.SimpleJSONRPCServer, JSONRPCDispatcher, object):

	owner = None
	
	def __init__(self, addr, requestHandler = JSONRPCRequestHandler, logRequests = True, source = None):
		self.owner = source
		super(JSONRPCServer, self).__init__(addr, requestHandler, logRequests)
	
