#! /usr/bin/python
# -*- coding: utf-8 -*-
#

from application import module
from application import agent as _agent
from libraries import irclib

import threading
import time
import sys

import Queue

class Module(module.AbstractModule):

	thread = None
	channels = None
	targets = None
	
	__password = None
	
	def __init__(self, application):
		super(Module, self).__init__(application)
		
		self.channels = {}
		self.targets = {}
	
	def initialize(self):
		
		self.__password = self.configuration.get("interaction", "password", "")
		
		###
		
		self.thread = _IRCThread(self)
		self.thread.start()
		
		# Registers global 'ircgate' function to RPC agents
		for agent in self.application.agents.values():
			if isinstance(agent, _agent.AbstractRPCAgent):
				callback = lambda source, target, message, password = None: self.application.api.message(source, Message(target, message, password))
				agent.register_function(callback, "ircgate")
				
		# Loads targets configuration
		for section in self.configuration.sections():
			target_channels = []
			
			if section.startswith("target."):
				target = section[len("target."):]
				items = self.configuration.items(section)
				
				for key, item in items:
				
					if item[0] == "#":
						self.channels[item] = True
						
					target_channels.append(item)
					
				self.targets[target] = target_channels
				
	def uninitialize(self):
		self.thread.disconnect_event.set()
		self.thread.done_event.wait(10)
		
	def handle(self, message):
		if isinstance(message.content, Message) and self.is_password_done(message.content.password):
			self.thread.queue.put(message.content, True, 10)
				
	def is_password_done(self, password):
		return (self.__password and (password == self.__password)) or not self.__password
			
class Message:
	target = None
	content = None
	password = None
	
	def __init__(self, target, content, password = None):
		self.target = target
		self.content = content
		self.password = password
		
		
class _IRCThread(threading.Thread):

	disconnect_event = threading.Event()
	done_event = threading.Event()
	
	queue = None
	parent = None
	connection = None
	irc = None
	
	def __init__(self, parent):
	
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self.parent = parent
		
		queue_size = self.parent.application.configuration.getint("queue", "size", 100000)		
		self.queue = Queue.Queue(queue_size)
		
	def run(self):
		
		pooling_interval = self.parent.application.pooling_interval
	
		###
		
		self.irc = irclib.IRC()
		self.connect()
		
		self.connection.add_global_handler("welcome", self.on_connect)
		self.connection.add_global_handler("disconnect", self.on_disconnect)
		self.connection.add_global_handler("privmsg", self.on_privmsg)
		self.connection.add_global_handler("pubmsg", self.on_pubmsg)		
		
		while not self.disconnect_event.is_set():
			self.irc.process_once()
		
			while not self.queue.empty():
				try:
					message = self.queue.get(False)
					self.send_targets(message.target, message.content)
				except Queue.Empty:
					break
								
			time.sleep(pooling_interval)
		
		###
		
		if self.parent.application.reloading:
			quit_message = self.parent.configuration.get("interaction", "reloading_message", "Reloading.")
		else:
			quit_message = None
			
		self.disconnect(quit_message)
		
		
	def send_targets(self, targets, message):
		if isinstance(targets, str):
			targets = [targets]

		for target in targets:
			if target in self.parent.targets:
				items = self.parent.targets[target]
				
				for item in items:
					if ((item in self.parent.channels) and self.parent.channels[item]) or not (item in self.parent.channels):
						self.connection.privmsg(item, message)
			
		
	def join(self, channels):
		
		if isinstance(channels, str):
			channels = [channels]
			
		for channel in channels:
			self.connection.join(channel)
			
		
	def disconnect(self, message = None):
		if message is None:
			quit_message = self.parent.configuration.get("interaction", "quit_message", "Bye!")
		else:
			quit_message = message
	
		try:
			self.connection.quit(quit_message)
			self.connection.disconnect()
		finally:
			self.done_event.set()
		
	def connect(self):
	
		configuration = self.parent.configuration
		
		server = configuration.get("connection", "server", "irc.freenode.net")
		port = configuration.getint("connection", "port", 6667)
		username = configuration.get("connection", "username", "ircbot")
		password = configuration.get("connection", "password", "")
		ipv6 = configuration.getboolean("connection", "ipv6", False)
		ssl = configuration.getboolean("connection", "ssl", False)

		###
		
		while True:
			try:	
				self.connection = self.irc.server().connect(server, port, username, ipv6 = ipv6, ssl = ssl)
				break
				
			except irclib.ServerConnectionError:
				sys.stderr.write("Connection failed. Sleeping 20 seconds and then reconnect.\n")
				time.sleep(20)
				
	###
		
	def on_connect(self, connection, event):
		self.join(self.parent.channels)
		
	def on_disconnect(self, connection, event):
		if not self.disconnect_event.is_set():
			self.connect()
			
	def on_pubmsg(self, connection, event):

		message = event.arguments()[0].strip().split(":", 1)
		target_user = message[0].strip()
		
		if target_user == connection.get_nickname():
			message = message[1].strip()
		else:
			return
		
		message = message.split(" ", 1)
		source = event.source().split("!", 1)[0].strip()
		target = event.target()		
			
		###

		try:

			if message[0] == "off":
		
#				password = None
#			
#				if len(message) >= 2:
#					password = message[1].strip()

				if True: #self.parent.is_password_done(password):
					self.parent.channels[target] = False
					self.connection.privmsg(target, "%s: OK, off" % (source))
			
			elif message[0] == "on":
		
#				password = None
#			
#				if len(message) >= 2:
#					password = message[1].strip()

				if True: #self.parent.is_password_done(password):
					self.parent.channels[target] = True
					self.connection.privmsg(target, "%s: OK, on" % (source))
					
			elif message[0] == "status":
				if self.parent.channels[target]:
					status = "on"
				else:
					status = "off"
					
				self.connection.privmsg(target, "%s: %s" % (source, status))
				

				
		except:
			sys.stderr.write(source, "FAILED, exception: %s\n" % str(sys.exc_value))		
		
				
	def on_privmsg(self, connection, event):

		if event.target() == connection.get_nickname():
			message = event.arguments()[0].strip().split(" ", 1)
			
		source = event.source().split("!", 1)[0].strip()
			
		###
		
		try:
		
			if message[0] == "shutdown":
		
				password = None
			
				if len(message) >= 2:
					password = message[1].strip()
						
				module = self.parent.application.loads.modules["system"]
				bus_message = module.Message(module.Message.SHUTDOWN, password)
				self.parent.application.api.message(self.parent, bus_message)
			
				self.connection.privmsg(source, "OK, i'm going to shutdown")
			
			elif message[0] == "reload":
		
				password = None
			
				if len(message) >= 2:
					password = message[1].strip()
						
				module = self.parent.application.loads.modules["system"]
				bus_message = module.Message(module.Message.RELOAD, password)
				self.parent.application.api.message(self.parent, bus_message)
			
				self.connection.privmsg(source, "OK, i'm going to reload")
				
		except:
			self.connection.privmsg(source, "FAILED, exception: " + str(sys.exc_value))



###
				
def factory(application):
	return Module(application)

