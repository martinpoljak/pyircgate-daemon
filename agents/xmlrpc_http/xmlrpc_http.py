#! /usr/bin/python
# -*- coding: utf-8 -*-
#

from application import agent
from application.rpc import xml

import time
import threading
import socket
import sys

class Agent(agent.AbstractRPCAgent):

	server = None
	
	__shutdown_event = threading.Event()
	__done_event = threading.Event()	
	
	def run(self):
		
		if not self.configuration.getboolean("server", "enabled", True):
			return
			
		###

		host = self.configuration.get("server", "interface", "")
		port = self.configuration.getint("server", "port", 8000)
		allow_none = self.configuration.getboolean("xml-rpc", "allow_none", True)
		
		pooling_interval = self.application.pooling_interval
		
		###
		
		self.server = xml.XMLRPCServer((host, port), allow_none = allow_none, source = self)
		self.server.timeout = pooling_interval
		
		self.server.register_introspection_functions()
		self.server.register_instance(self.application.api)
		
		for callback, alias in self._additional_api:
			self.server.register_function(callback, alias)
			
		self._run = True
		
		while not self.__shutdown_event.is_set():
			self.server.handle_request()
			
		self.__shutdown_event.clear()
		
		self.__done_event.set()
		self.__done_event.clear()
		
		try:
			self.server.socket.shutdown(socket.SHUT_RDWR)
		except socket.error:
			pass
		
#		sys.exit()
		
	def uninitialize(self):
		self.__shutdown_event.set()
		self.__done_event.wait(10)
		
#		try:
#			self.server.socket.shutdown(socket.SHUT_RDWR)
#		except socket.error:
#			pass
			
		self.__done_event.clear()


def factory(application):
	return Agent(application)
