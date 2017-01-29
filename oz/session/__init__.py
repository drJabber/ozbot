import time
import logging
from datetime import datetime

import sessionmanager

class Session(object):
	def __init__(self, sid):
		super(Session, self).__init__()

		self.sid = sid
		self.start_time = time.time() ##.session

		self.user_nickname = 'none'
		self.state = 'location'
		self.location = {'latitude':0.0, 'longitude':0.0 }

		self.source_page = 0
		self.source_stations = [ ]
		self.source_station = 0

		self.dest_page = 0

	def initialize(self):
		self.state = 'location'
		self.location = {'latitude':0.0, 'longitude':0.0 }

		self.source_page = 0
		self.source_stations = [ ]
		self.source_station = 0

		self.dest_page = 0

	def get_actions(self):
		if self.state=='location':
			return get_location_actions(self)


	def get_source_stations(self, location):
		self.location=location
		return get_source_actions(self)


	def message(self, reply, text):
		if self.state=='source':
			source_selected(self,reply,text)
		elif self.state=='direction':
			direction_selected(self,reply,text)
		elif self.state=='schedule':
			schedule_item_selected(self,reply,text)
		elif self.state=='thread':
			thread_item_selected(self,reply,text)
		return False


from session.location_definition import get_location_actions
from session.source_definition import get_source_actions
from session.dest_definition import source_selected,direction_selected,schedule_item_selected,thread_item_selected
