import constants
import datetime as dt
import re
from action import Action

class StopItem(object):
	def __init__(self, json_item=None):
		if json_item:
			self.arrival=None
			self.departure=None

			self.duration=json_item["duration"]

			dtt=json_item["arrival"]
			if dtt:
				self.arrival=dt.datetime.strptime(dtt,"%Y-%m-%d %H:%M:%S")

			dtt=json_item["departure"]
			if dtt:
				self.departure=dt.datetime.strptime(dtt,"%Y-%m-%d %H:%M:%S")

			self.short_title=json_item['station']['short_title']
			self.title=json_item['station']['title']
			self.popular_title=json_item['station']['popular_title']


		else:
			self.title=''
			self.short_title=''
			self.popular_title=''

			self.arrival=None
			self.departure=None
			self.duration=0.0


