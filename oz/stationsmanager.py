import logging
import constants
import requests
import json
import datetime as dt
#from oz.oz_database import db
from station import Station
from scheduleitem import ScheduleItem
from oz_application import app

def load_source_stations(session):
	rq_text="https://api.rasp.yandex.net/v1.0/nearest_stations/?apikey=" + app.config['YANDEX_TOKEN'] +  \
                "&format=json&lang=ru&transport_types=train" + \
                "&lat={0:0.15f}&lng={1:0.15f}&distance={2:0.3f}".format(session.location.latitude,session.location.longitude,constants.MAX_DISTANCE)

#	app.logger.info(rq_text)
	rq=requests.get(rq_text)
#	app.logger.info(json.dumps(rq.json(), indent=4))
	stations=[ ]
	for rq_item in rq.json()["stations"]:
		stations.append(Station(rq_item))

	return stations

def load_directions(code):

	rq_text="https://api.rasp.yandex.net/v1.0/schedule/?apikey=" + app.config['YANDEX_TOKEN'] +  \
                "&format=json&station=" + code + \
                "&lang=ru" + \
                "&transport_types=suburban" + \
                "&system=yandex&date=" + dt.datetime.today().strftime('%Y-%m-%d')

#	app.logger.info(rq_text)

	rq=requests.get(rq_text)

#	app.logger.info(json.dumps(rq.json(), indent=4))

	directions= [ ] 
	for rq_item in rq.json()["directions"]:
		if rq_item not in ['all','arrival']:
			directions.append(rq_item)

	app.logger.info(directions)

	return directions


