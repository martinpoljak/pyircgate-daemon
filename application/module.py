#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import abc
import component

class AbstractModule(component.AbstractComponent):
			
	basepath = ""
	
	def __init__(self, application):
	
		self.basepath = application.configuration.get("paths", "modules")
		super(AbstractModule, self).__init__(application)
		
	@abc.abstractmethod
	def handle(self, message):
		pass
	

