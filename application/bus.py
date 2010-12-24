#! /usr/bin/python
# -*- coding: utf-8 -*-
#

class Bus:
	listeners = None
	
	def __init__(self):
		self.listeners = []
			
	def handle(self, message):
		for listener in self.listeners:
			terminate = listener.handle(message)
			
			if terminate:
				break
		
	def register(self, listener):
		self.listeners.append(listener)
