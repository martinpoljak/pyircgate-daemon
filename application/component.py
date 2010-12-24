#! /usr/bin/python
# -*- coding: utf-8 -*-
#

from libraries import INIParser

class AbstractComponent(object):
	
	application = None
	configuration = None
	
	path = ""
	name = ""
	
	basepath = ""
	
	def __init__(self, application):
	
		self.application = application
		self.name = self.__class__.__module__
		self.path = "%s/%s" % (self.basepath, self.name)
		
		self.configuration = INIParser.INIParser()
		self.configuration.read("%s/%s.ini" % (self.path, self.name))
		
	def initialize(self):
		pass
			
	def uninitialize(self):
		pass

	

