#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import sys
import os
import imp
import time
import atexit
import gc

import Queue
import ConfigParser

from application import bus, api
from libraries import INIParser

class _Loads:
	agents = {}
	modules = {}

class Application:

	configuration = INIParser.INIParser()	
	
	agents = None
	modules = None
	queue = None
	bus = None
	api = None
	system = None
	
	loads = _Loads()
	
	pooling_interval = 0.1
	reloading = None
	
	def __init__(self):
	
		self.reloading = False	
	
		self.agents = {}
		self.modules = {}
				
		self.configuration.read("./preferences.ini")	
		queue_size = self.configuration.getint("queue", "size", 100000)
		
		self.pooling_interval = self.configuration.getfloat("internal", "pooling_interval", self.pooling_interval)
		
		###
			
		self.bus = bus.Bus()
		self.queue = Queue.Queue(queue_size)
		self.api = api.API(self)
		
		###
		
#		atexit.register(lambda: self.shutdown())	
		gc.collect()

	def run(self):
	
		pooling_interval = self.configuration.getfloat("internal", "pooling_interval", 0.1)
		system_module = self.configuration.get("internal", "system_module", "system")
		modules_path = self.configuration.get("paths", "modules", "./modules")
	
		###

		self.system = self.load_module(system_module, "%s/%s" % (modules_path, system_module))

		self.load_modules()
		self.load_agents()
		
		self.run_modules()
		self.run_agents()
		
		while True:
			while not self.queue.empty():
				try:
					self.bus.handle(self.queue.get(False))
				except Queue.Empty:
					break
			
			time.sleep(pooling_interval)
		
	def shutdown(self):
		for agent in self.agents.values():
			agent.uninitialize()
		for module in self.modules.values():
			module.uninitialize()

		sys.exit()
		
	def reload(self):
		self.reloading = True
		self.shutdown()
		
	def load_component(self, name, path, storage, loads):

		if name not in storage:
			filename, pathname, description = imp.find_module(name, [path])
			
			module = imp.load_module(name, filename, pathname, description)
			loads[name] = module
			
			instance = module.factory(self)
			storage[name] = instance
			
		else:
			instance = storage[name]
			
		return instance
		
	def load_components(self, path, loader):
		dirs = os.listdir(path)
		
		for item in dirs:
			dirpath = path + "/" + item
			
			if not item.endswith(".off") and os.path.isdir(dirpath):
				try:
					loader(item, dirpath)
				except:
					raise
					sys.stderr.write("WARNING: While importing '%s/%s' component: %s. Component ignored.\n" % (path, item, sys.exc_value))	
		
	def load_module(self, name, path):
		return self.load_component(name, path, self.modules, self.loads.modules)
		
	def load_agent(self, name, path):
		return self.load_component(name, path, self.agents, self.loads.agents)
		
	def load_agents(self):
		
		path = self.configuration.get("paths", "agents", "./agents")
		loader = lambda item, dirpath: self.load_agent(item, dirpath)
		
		self.load_components(path, loader)
						
		
	def load_modules(self):
		
		path = self.configuration.get("paths", "modules", "./modules")
		loader = lambda item, dirpath: self.load_module(item, dirpath)
		
		self.load_components(path, loader)

	
	def run_agents(self):
		for agent in self.agents.values():
			agent.initialize()
			agent.start()
			
	def run_modules(self):
		self.system.initialize()
		self.bus.register(self.system)
		
		for module in self.modules.values():
			if module is not self.system:
				module.initialize()
				self.bus.register(module)

		
if __name__ == "__main__":
	while True:
		try:
			application = Application()
			application.run()
			
		except SystemExit:
			if not application.reloading:
				print "Shutting down."			
				raise
			else:
				print "Reloading."
				application.reloading = False
				
				continue
	
	
