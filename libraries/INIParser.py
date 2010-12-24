#! /usr/bin/python
# -*- coding: utf-8 -*-
#

import sys

import ConfigParser

class INIParser(ConfigParser.RawConfigParser, object):
	
	def __get_default(self, section, option, default, getter):
	
		try:
			value = getter(section, option)
			
		except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
		
			if default is not None:
				value = default
			else:
				raise 
				
		return value
		
	def __fix_string(self, string):
	
		if len(string) > 2:
			if ((string[0] == "\"") and (string[-1] == "\"")) or ((string[0] == "'") and (string[-1] == "'")):
				string = string[1:-1]		
		
		return string

	def get(self, section, option, default = None):

		getter = lambda section, option: super(INIParser, self).get(section, option)
		value = self.__get_default(section, option, default, getter)
		
		value = self.__fix_string(value)			
		return value
	
	def getint(self, section, option, default = None):
		getter = lambda section, option: super(INIParser, self).getint(section, option)
		return self.__get_default(section, option, default, getter)
		
	def getfloat(self, section, option, default = None):
		getter = lambda section, option: super(INIParser, self).getfloat(section, option)
		return self.__get_default(section, option, default, getter)
		
	def getboolean(self, section, option, default = None):
		getter = lambda section, option: super(INIParser, self).getboolean(section, option)
		return self.__get_default(section, option, default, getter)

	def items(self, section):
		section_items = super(INIParser, self).items(section)
		result = []
		
		for key, item in section_items:
			if isinstance(item, str):
				item = self.__fix_string(item)
				
			result.append((key, item))
				
		return result
