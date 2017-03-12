import constants
import requests
import json
import datetime as dt
#from oz.oz_database import db
from scheduleitem import ScheduleItem
from oz_application import app
from stopitem import StopItem

def load_schedule(code, direction):
	schedule=[ ]

	now=dt.datetime.now()

	rq_text="https://api.rasp.yandex.net/v1.0/schedule/?apikey=" + app.config['YANDEX_TOKEN'] + \
                         "&format=json&station=" + code + \
                         "&lang=ru&transport_types=suburban&event=departure&system=yandex"

	if direction:
		rq_text=rq_text+"&direction="+direction

	rq=requests.get(rq_text+"&date=" + now.strftime('%Y-%m-%d'))

	rqj=rq.json()
	if 'schedule' in rqj:
		rq_schedule = rqj["schedule"]


#		trips today after now
		for sh_item in rq_schedule:
			item=ScheduleItem(sh_item)
			dtt=item.departure
			if item.arrival:
				dtt=item.arrival
			if dtt>now:
				schedule.append(item)

	rq=requests.get(rq_text+"&date=" + (now+dt.timedelta(days=1)).strftime('%Y-%m-%d'))

	rqj=rq.json()
	if 'schedule' in rqj:
		rq_schedule = rqj["schedule"]

#		trips tomorrow before this time
		for sh_item in rq_schedule:
			item=ScheduleItem(sh_item)
			dtt=item.departure
			if item.arrival:
				dtt=item.arrival
			if dtt<=(now+dt.timedelta(days=1)):
				schedule.append(item)

	return schedule

def load_custom_schedule(source_code, target_code):
	schedule=[ ]

	now=dt.datetime.now()

	rq_text="https://api.rasp.yandex.net/v1.0/search/?apikey=" + app.config['YANDEX_TOKEN'] + \
                         "&format=json&from=" + source_code + \
                         "&to="+target_code +\
                         "&lang=ru&transport_types=suburban&event=departure&system=yandex"

	rq=requests.get(rq_text+"&date=" + now.strftime('%Y-%m-%d'))

	rqj=rq.json()
	if 'threads' in rqj:
		rq_schedule = rqj["threads"]


#		trips today after now
		for sh_item in rq_schedule:
			item=ScheduleItem(sh_item)
			dtt=item.departure
			if item.arrival:
				dtt=item.arrival
			if dtt>now:
				schedule.append(item)

	rq=requests.get(rq_text+"&date=" + (now+dt.timedelta(days=1)).strftime('%Y-%m-%d'))

	rqj=rq.json()
	if 'threads' in rqj:
		rq_schedule = rqj["threads"]

#			trips tomorrow before this time
		for sh_item in rq_schedule:
			item=ScheduleItem(sh_item)
			dtt=item.departure
			if item.arrival:
				dtt=item.arrival
			if dtt<=(now+dt.timedelta(days=1)):
				schedule.append(item)

	return schedule

def load_thread_stops(schedule_item, station):
	now=dt.datetime.now()

	rq_text="https://api.rasp.yandex.net/v1.0/thread/?apikey=" + app.config['YANDEX_TOKEN'] + \
                         "&format=json&uid=" + schedule_item.uid + \
                         "&lang=ru"

	rq=requests.get(rq_text+"&date=" + now.strftime('%Y-%m-%d'))
	rq_stops = rq.json()["stops"]

	idx=0
	for stop in rq_stops:
		if stop["station"]["code"]!=station.yandex_code:
			idx+=1
		else:
			 break

	stops=[ ]
	for stop in rq_stops[idx:] :
		stops.append(StopItem(stop))

	return stops