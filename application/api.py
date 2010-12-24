#! /usr/bin/python
# -*- coding: utf-8 -*-
#

from application import message as _message

class API:

	application = None
	__queue_timeout = 10
	
	def __init__(self, application):
		self.application = application
		self.__queue_timeout = application.configuration.getint("queue", "timeout", self.__queue_timeout)
		
	def message(self, source, content):
		message = _message.Message(self, content)
		return self.application.queue.put(message, True, self.__queue_timeout)

