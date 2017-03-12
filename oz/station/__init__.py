import constants
import datetime as dt
from action import Action

from oz_application import app

class Station(object):
	def __init__(self, row=None):
		if row:
			self.distance=row["distance"]
			self.yandex_code=row["code"]
			self.yandex_name=row["title"]
			self.popular_name=row["popular_title"]
			self.short_name=row["short_title"]

			self.longitude=row['lng']
			self.latitude=row['lat']

			self.directions=None
			self.direction=-1

			self.schedule=None
			self.schedule_index=0
			self.schedule_page=0

		else:
			self.distance=-1
			self.yandex_code=''
			self.yandex_name=''
			self.popular_name=''
			self.short_name=''


			self.directions=None
			self.direction=-1

			self.schedule=None
			self.schedule_index=0
			self.schedule_page=0

	def get_direction_actions(self):
		self.directions=load_directions(self.yandex_code)
		actions=[ ]
		if len(self.directions)>0:
			idx=0
			for direction in self.directions:
				action = Action('{0:d}-{1:s}'.format(idx+1,direction),{constants.ACTION_FLAG_REQUEST_NONE})
				actions.append(action)
				idx+=1

			actions.append(Action('<<Ближайшие станции',{constants.ACTION_FLAG_REQUEST_NONE}))
			actions.append(Action('>>Новое положение<<',{constants.ACTION_FLAG_REQUEST_LOCATION}))

		return actions

	def get_schedule_actions(self):
		actions=[ ]

		direction=None
		if self.direction>=0:
			direction=self.directions[self.direction]

		self.schedule=load_schedule(self.yandex_code,direction)

		now=dt.datetime.now()

		if len(self.schedule)>0:
			start=min(self.schedule_page*constants.SCHEDULE_PAGE_SIZE, len(self.schedule)-1)
			finish=min((self.schedule_page+1)*constants.SCHEDULE_PAGE_SIZE, len(self.schedule))

			idx=0
			for schedule_item in self.schedule[start:finish]:
				if schedule_item:
					tm=schedule_item.arrival
					if tm.time()>now.time():
						fmt='{0:d} -   {1:s} - {2:s}'
					else:
						fmt='{0:d} - + {1:s} - {2:s}'
					action = Action(fmt.format(idx+1,schedule_item.arrival.strftime('%H:%M'),schedule_item.destination_title),{constants.ACTION_FLAG_REQUEST_NONE})
					actions.append(action)
				idx+=1

			if finish<len(self.schedule):
				actions.append(Action('Вперед>>',{constants.ACTION_FLAG_REQUEST_NONE}))

			if start>0:
				actions.append(Action('<<Назад',{constants.ACTION_FLAG_REQUEST_NONE}))
			else:
				if direction:
					actions.append(Action('<<Направления',{constants.ACTION_FLAG_REQUEST_NONE}))
				else:
					actions.append(Action('<<Ближайшие станции',{constants.ACTION_FLAG_REQUEST_NONE}))


		actions.append(Action('>>Новое положение<<',{constants.ACTION_FLAG_REQUEST_LOCATION}))

		return actions


from stationsmanager import load_directions
from schedulemanager import load_schedule
