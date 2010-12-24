#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import re

from application import module
from application import agent as _agent

class Module(module.AbstractModule):

	__password = None
	
	def initialize(self):
	
		self.__password = self.configuration.get("interaction", "password", "")	
				
		# Registers global functions to RPC agents
		for agent in self.application.agents.values():
			if isinstance(agent, _agent.AbstractRPCAgent):
			
				# Shutdown
				callback = lambda source, password = None: self.application.api.message(source, Message(Message.SHUTDOWN, password))
				agent.register_function(callback, "shutdown")
				
				# Reload
				callback = lambda source, password = None: self.application.api.message(source, Message(Message.RELOAD, password))
				agent.register_function(callback, "reload")
				
	
	def handle(self, message):
	
		if isinstance(message.content, Message):
		
			if (self.__password and (message.content.password == self.__password)) or not self.__password:
		
				if message.content.type == Message.SHUTDOWN:
					self.application.shutdown()
					return True 	# terminate further message processing by bus
				
				elif message.content.type == Message.RELOAD:
					self.application.reload()
					return  	# terminate further message processing by bus

class Message:
	type = None
	password = None
	
	SHUTDOWN = 1
	RELOAD = 2
	
	def __init__(self, type, password = None):
		self.type = type
		self.password = password

				
def factory(application):
	return Module(application)
