import constants
import datetime as dt
import re
from action import Action

class ScheduleItem(object):
	def __init__(self, json_item=None):
		if json_item:
			self.uid=json_item['thread']['uid']

			self.arrival=None
			arvl=json_item["arrival"]
			if arvl:
				self.arrival=dt.datetime.strptime(arvl,"%Y-%m-%d %H:%M:%S")

			self.departure=None
			dptr=json_item["departure"]
			if dptr:
				self.departure=dt.datetime.strptime(dptr,"%Y-%m-%d %H:%M:%S")

			self.number=json_item['thread']['number']
			self.short_title=json_item['thread']['short_title']
			self.destination_title=self.extract_destination(self.short_title)

			self.stops=json_item['stops']

			self.days=''
			if 'days' in json_item:
				self.days=json_item['days']

			self.except_days=''
			if 'except_days' in json_item:
				self.except_days=json_item['except_days']

			self.is_fuzzy=False
			if 'is_fuzzy' in json_item:
				self.iz_fuzzy=json_item['is_fuzzy']

			self.platform=''
			if 'platform' in json_item:
				self.platform=json_item['platform']

			self.from_title=''
			if 'from' in json_item:
				self.from_title=json_item['from']['title']

			self.to_title=''
			if 'to' in json_item:
				self.to_title=json_item['to']['title']

			self.stops=None
			self.stops_page=0
			self.stop_index=0

		else:
			self.uid=''

			self.arrival=None
			self.departure=None

			self.number=''
			self.short_title=''
			self.destination_title=''

			self.stops=''
			self.days=''
			self.except_days=''

			self.is_fuzzy=False
			self.platform=''

			self.from_title=''
			self.to_title=''

			self.stops=None
			self.stops_page=0
			self.stop_index=0


	def extract_destination(self,title):
		g=re.search(' \u2014 (.*)',title,re.UNICODE)
		if g:
			return g.group(1)
		else:
			return ""


	def get_stop_actions(self, station):
		actions=[ ]

		self.stops=load_thread_stops(self, station)

		now=dt.datetime.now()

		if len(self.stops)>0:
			start=min(self.stops_page*constants.SCHEDULE_PAGE_SIZE, len(self.stops)-1)
			finish=min((self.stops_page+1)*constants.SCHEDULE_PAGE_SIZE, len(self.stops))

			idx=0
			for stop in self.stops[start:finish]:
				if stop:
					tm=stop.arrival
					if tm:
						if tm.time()>now.time():
							fmt='{0:d} -   {1:s} - {2:s}'
						else:
							fmt='{0:d} - + {1:s} - {2:s}'
					else:
						tm=stop.departure
						if tm.time()>now.time():
							fmt='{0:d} -   {1:s} - {2:s}'
						else:
							fmt='{0:d} - + {1:s} - {2:s}'

					action = Action(fmt.format(idx+1,tm.strftime('%H:%M'),stop.title),{constants.ACTION_FLAG_REQUEST_NONE})
					actions.append(action)
				idx+=1

			if start>0:
				actions.append(Action('<<Назад',{constants.ACTION_FLAG_REQUEST_NONE}))
			else:
				actions.append(Action('<<Расписание',{constants.ACTION_FLAG_REQUEST_NONE}))

			if finish<len(self.stops):
				actions.append(Action('Вперед>>',{constants.ACTION_FLAG_REQUEST_NONE}))

		actions.append(Action('>>Новое положение<<',{constants.ACTION_FLAG_REQUEST_LOCATION}))

		return actions


from schedulemanager import load_thread_stops
