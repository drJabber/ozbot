import time
import logging
from datetime import datetime
from collections import deque

import sessionmanager as sm
from oz.utils import telegram_trace

class Session(object):
	def __init__(self, sid):
		super(Session, self).__init__()

		self.target=''
		self.sid = sid
		self.start_time = time.time() ##.session

		self.user_nickname = 'none'
		self.state = 'location'
		self.last_state = self.state
		self.location = {'latitude':0.0, 'longitude':0.0 }

		self.source_page = 0
		self.source_stations = [ ]
		self.source_station = -1

		self.custom_destination_page=0
		self.custom_destinations= []
		self.custom_destination=-1
		self.custom_destination_pattern=''

		self.custom_schedule = [ ]
		self.custom_schedule_page = 0
		self.custom_schedule_index=-1

	def initialize(self, state):
		self.state = state
		self.location = {'latitude':0.0, 'longitude':0.0 }

		self.source_page = 0
		self.source_stations = [ ]
		self.source_station = -1

		self.last_state = state
		self.custom_destination_pattern=''
		self.custom_destination_page=0
		self.custom_destinations= []
		self.custom_destination=-1

		self.custom_schedule = [ ]
		self.custom_schedule_page = 0
		self.custom_schedule_index=-1

	def get_actions(self):
		if self.state=='location':
			return get_location_actions(self)

	def get_source_station(self):
		return self.source_stations[self.source_station]

	def get_custom_schedule_item(self):
		return self.custom_schedule[self.custom_schedule_index]

	def get_custom_destination(self):
		return self.custom_destinations[self.custom_destination]

	def get_source_station_name(self):
		return self.get_source_station().yandex_name

	def get_custom_destination_name(self):
		return self.get_custom_destination()[1]

	def get_custom_destination_code(self):
		return self.get_custom_destination()[0]

	def set_state(self, state):
		self.save_current_state()
		self.state=state

	def save_current_state(self):
		if self.state!='custom_destination':
			self.last_state=self.state

	def restore_state(self,reply):
		self.state=self.last_state
		if self.state=='location':
			sm.show_source_stations_page(self,self.location,reply)
		elif self.state=='source':
			sm.show_source_directions(self,self.source_station,reply)
		elif self.state=='direction':
			sm.show_source_direction_schedule(self,self.source_stations[self.source_station].direction,reply)
		elif self.state=='schedule':
			sm.show_schedule_page(self,reply)
		elif self.state=='thread':
			sm.show_thread_stops_page(self,reply)

	def get_source_stations(self, location):
		self.location=location
		return get_source_actions(self)

	def get_custom_destination_actions(self):
		return get_custom_destination_actions(self)

	def get_custom_schedule_actions(self):
		return get_custom_schedule_actions(self)

	def message(self, reply, text):
		telegram_trace(reply,'state='+self.state+';last-state='+self.last_state+'; text='+text)

		if self.state=='location':
			location_not_selected(self,reply)
		elif self.state=='source':
			source_selected(self,reply,text)
		elif self.state=='direction':
			direction_selected(self,reply,text)
		elif self.state=='schedule':
			schedule_item_selected(self,reply,text)
		elif self.state=='custom_schedule':
			custom_schedule_item_selected(self,reply,text)
		elif self.state=='thread':
			thread_item_selected(self,reply,text)
		elif self.state=='custom_destination':
			custom_destination_selected(self,reply,text)
		elif self.state=='custom_schedule':
			custom_schedule_item_selected(self,reply,text)
		return False


from session.location_definition import get_location_actions, location_not_selected
from session.source_definition import get_source_actions
from session.dest_definition import source_selected,direction_selected,schedule_item_selected,thread_item_selected,custom_destination_selected,custom_schedule_item_selected
from session.custom_definition import get_custom_destination_actions, get_custom_schedule_actions
