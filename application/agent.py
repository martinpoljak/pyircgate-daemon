#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import abc
import threading
import component

class AbstractAgent(component.AbstractComponent, threading.Thread):
	
	def __init__(self, application):
	
		self.basepath = application.configuration.get("paths", "agents")	
		super(AbstractAgent, self).__init__(application)
		
		threading.Thread.__init__(self)
		self.setDaemon(True)
		
	def take(self, message):
		return self.application.api.message(self, message)
		
	@abc.abstractmethod
	def run(self):
		pass
	
class AbstractRPCAgent(AbstractAgent):

	_additional_api = []
	_run = False
	
	def register_function(self, callback, name = None):
		if not self._run:
			self._additional_api.append((callback, name))
		else:
			raise RPCAgentException("Agent is run. Further additional API extending isn't possible.")
			
class RPCAgentException(Exception):
	pass
