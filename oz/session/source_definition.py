import constants

from action import Action
from station import Station

from oz.stationsmanager import load_source_stations

def get_source_actions(self):
	if self.state=='location':
		self.source_stations=load_source_stations(self)
	
	actions=[ ]
	if len(self.source_stations)>0:
		start=min(self.source_page*constants.STATIONS_PAGE_SIZE, len(self.source_stations)-1)
		finish=min((self.source_page+1)*constants.STATIONS_PAGE_SIZE, len(self.source_stations))
		
		idx=0
		for station in self.source_stations[start:finish]:
			if station is not None:
				action = Action('{0:d}-{1:s} ({2:0.2f}км)'.format(idx+1,station.yandex_name,station.distance),{constants.ACTION_FLAG_REQUEST_NONE})
				actions.append(action)
			idx+=1

		if finish<len(self.source_stations):
			actions.append(Action('Вперед>>',{constants.ACTION_FLAG_REQUEST_NONE}))

		if start>0:
			actions.append(Action('<<Назад',{constants.ACTION_FLAG_REQUEST_NONE}))

	actions.append(Action('>>Новое положение<<',{constants.ACTION_FLAG_REQUEST_LOCATION}))

	return actions
