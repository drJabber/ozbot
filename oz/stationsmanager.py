import logging
import constants
import requests
import json
import datetime as dt
import sqlalchemy as sa

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


def find_station_in_db(station, current_location):
	engine=sa.create_engine('postgresql+psycopg2://ozbot@localhost/ozbot')
	connection = engine.connect()
	sql='select id, name_esr, name_express, name_osm,esr,express, location '+ \
		'from rzd.stations ' + \
		'where upper(name_esr) like upper(\'%{0:s}%\') or upper(name_express) like upper(\'%{0:s}%\') or upper(name_osm) like upper(\'%{0:s}%\') ' + \
		'order by ST_Distance(location,ST_GeogFromText(\'SRID=4326;POINT({1:0.8f} {2:0.8f})\')) asc '
	sql_f=sql.format(station, current_location.longitude, current_location.latitude)
	
	result=engine.execute(sa.text(sql_f))

	r=[]
	for row in result:
		express=row['express']
		if  express and express!='':
			r.append(express)
	
	connection.close()

	return r


def load_custom_destinations(session):
	found_stations=find_station_in_db(session.custom_destination_pattern, session.location)
	yandex_stations=[]

	for s in found_stations:
		r = requests.get("https://api.rasp.yandex.net/v1.0/schedule/?" +
				    "apikey=" + app.config['YANDEX_TOKEN'] +
				    "&format=json" +
				    "&station=" + s +
				    "&lang=ru" +
				    "&transport_types=suburban" +
				    "&event=arrival"+
				    "&date=" + dt.datetime.today().strftime('%Y-%m-%d')+
				    "&system=express" )
		try:
			ys=r.json()["station"]
			yandex_stations.append([ys["code"], ys["title"]])
		except:
			pass

	return yandex_stations