import constants
import datetime as dt

from action import Action
from station import Station

from oz.stationsmanager import load_custom_destinations
from oz.schedulemanager import load_custom_schedule

def get_custom_destination_actions(session):
	session.custom_destinations=load_custom_destinations(session)
	
	actions=[ ]
	if len(session.custom_destinations)>0:
		start=min(session.custom_destination_page*constants.STATIONS_PAGE_SIZE, len(session.custom_destinations)-1)
		finish=min((session.custom_destination_page+1)*constants.STATIONS_PAGE_SIZE, len(session.custom_destinations))
		
		idx=0
		for stn in session.custom_destinations[start:finish]:
			if stn is not None:
				action = Action('{0:d}-{1:s}'.format(idx+1,stn[1]),{constants.ACTION_FLAG_REQUEST_NONE})
				actions.append(action)
			idx+=1

		if finish<len(session.custom_destinations):
			actions.append(Action('Вперед>>',{constants.ACTION_FLAG_REQUEST_NONE}))

		if start>=0:
			actions.append(Action('<<Назад',{constants.ACTION_FLAG_REQUEST_NONE}))

	actions.append(Action('>>Новое положение<<',{constants.ACTION_FLAG_REQUEST_LOCATION}))

	return actions

def get_custom_schedule_actions(session):
	actions=[ ]

	session.custom_schedule=load_custom_schedule(session.get_source_station().yandex_code,session.get_custom_destination_code())

	now=dt.datetime.now()

	if len(session.custom_schedule)>0:
		start=min(session.custom_schedule_page*constants.SCHEDULE_PAGE_SIZE, len(session.custom_schedule)-1)
		finish=min((session.custom_schedule_page+1)*constants.SCHEDULE_PAGE_SIZE, len(session.custom_schedule))

		idx=0
		for schedule_item in session.custom_schedule[start:finish]:
			if schedule_item:
				tm=schedule_item.arrival
				if tm.time()>now.time():
					fmt='{0:d} -   {1:s} - {2:s}'
				else:
					fmt='{0:d} - + {1:s} - {2:s}'
				action = Action(fmt.format(idx+1,schedule_item.departure.strftime('%H:%M'),schedule_item.destination_title),{constants.ACTION_FLAG_REQUEST_NONE})
				actions.append(action)
			idx+=1

		if finish<len(session.custom_schedule):
			actions.append(Action('Вперед>>',{constants.ACTION_FLAG_REQUEST_NONE}))

		if start>0:
			actions.append(Action('<<Назад',{constants.ACTION_FLAG_REQUEST_NONE}))


	actions.append(Action('>>Новое положение<<',{constants.ACTION_FLAG_REQUEST_LOCATION}))

	return actions

