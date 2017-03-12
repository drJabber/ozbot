import constants
import re
import logging
import sessionmanager
from utils import telegram_trace

def source_selected(session, reply, text):
	idx=extract_index_in_page(text)
	if idx>0:
		session.source_station=session.source_page*constants.STATIONS_PAGE_SIZE+idx-1
		sessionmanager.show_source_directions(session,session.source_station,reply)
	elif idx==-2:
		session.source_page=max(session.source_page-1,0)
		sessionmanager.show_source_stations_page(session, session.location, reply)
	elif idx==-1:
		session.source_page=min(session.source_page+1,len(session.source_stations)//constants.STATIONS_PAGE_SIZE)
		sessionmanager.show_source_stations_page(session, session.location, reply)
	elif idx==0:
		sessionmanager.show_custom_destinations(session,reply,text)
		telegram_trace(reply,'sourceselected  after showcustomdest')

def direction_selected(session, reply, text):
	idx=extract_direction_index(text)
#	telegram_trace(reply,str(idx))
	if idx>0:
		sessionmanager.show_source_direction_schedule(session,idx-1,reply)
	elif idx==-2:
		sessionmanager.show_source_stations_page(session, session.location, reply)
	elif idx==0:
		sessionmanager.show_custom_destinations(session,reply,text)

def schedule_item_selected(session, reply, text):
	idx=extract_index_in_page(text)
	station=session.source_stations[session.source_station]
	if idx>0:
		station.schedule_index=station.schedule_page*constants.SCHEDULE_PAGE_SIZE+idx-1
		sessionmanager.show_thread_stops(session,idx-1,reply)
	elif idx==-2:
		if station.schedule_page>=1:
			station.schedule_page=max(station.schedule_page-1,0)
			sessionmanager.show_schedule_page(session, reply)
		else:
			sessionmanager.show_source_directions(session,session.source_station,reply)
	elif idx==-1:
		station.schedule_page=min(station.schedule_page+1,len(station.schedule)//constants.SCHEDULE_PAGE_SIZE)
		sessionmanager.show_schedule_page(session, reply)
	elif idx==0:
		sessionmanager.show_custom_destinations(session,reply,text)

def custom_destination_selected(session, reply, text):
	idx=extract_index_in_page(text)
	if idx>0:
		session.custom_destination=session.custom_destination_page*constants.STATIONS_PAGE_SIZE+idx-1
		if session.source_station>=0:
			sessionmanager.show_custom_schedule(session,reply)
		else:
			#если не выбрана станция отправления
			session.source_page=0
			sessionmanager.show_source_stations_page(session, session.location, reply)
	elif idx==-2:
		if session.custom_destination_page>=1:
			session.custom_destination_page=max(session.custom_destination_page-1,0)
			sessionmanager.show_custom_destinations_page(session, reply)
		else:
			sessionmanager.show_last_state(session,reply)
	elif idx==-1:
		session.custom_destination_page=min(session.custom_destination_page+1,len(session.custom_destinations)//constants.STATIONS_PAGE_SIZE)
		sessionmanager.show_custom_destinations_page(session, reply)
	elif idx==0:
		sessionmanager.show_custom_destinations(session,reply,text)

def custom_schedule_item_selected(session, reply, text):
	idx=extract_index_in_page(text)
	station=session.get_source_station()
	if idx>0:
		session.custom_schedule_index=session.custom_schedule_page*constants.SCHEDULE_PAGE_SIZE+idx-1
		sessionmanager.show_custom_info(session,reply)
	elif idx==-2:
		if session.custom_schedule_page>=1:
			session.custom_schedule_page=max(session.custom_schedule_page-1,0)
			sessionmanager.show_custom_schedule_page(session, reply)
	elif idx==-1:
		session.custom_schedule_page=min(session.custom_schedule_page+1,len(session.custom_schedule)//constants.SCHEDULE_PAGE_SIZE)
		sessionmanager.show_custom_schedule_page(session, reply)
	elif idx==0:
		sessionmanager.show_custom_destinations(session,reply,text)

def thread_item_selected(session, reply, text):
	idx=extract_index_in_page(text)
	station=session.source_stations[session.source_station]
	schedule_item=station.schedule[station.schedule_index]

	if idx>0:
		schedule_item.stop_index=schedule_item.stops_page*constants.SCHEDULE_PAGE_SIZE+idx-1
		sessionmanager.show_trip_message(session,schedule_item.stop_index,reply)
	elif idx==-2:
		if schedule_item.stops_page>=1:
			schedule_item.stops_page=max(schedule_item.stops_page-1,0)
			sessionmanager.show_thread_stops_page(session, reply)
		else:
			sessionmanager.show_schedule_page(session,reply)
	elif idx==-1:
		schedule_item.stops_page=min(schedule_item.stops_page+1,len(schedule_item.stops)//constants.SCHEDULE_PAGE_SIZE)
		sessionmanager.show_thread_stops_page(session, reply)
	elif idx==0:
		sessionmanager.show_custom_destinations(session,reply,text)


def extract_index_in_page(text):
	if text.startswith('<<') or text.startswith('«'):
		return -2
	elif text.endswith('>>'):
		return -1
	else:
		rr=re.findall('^\d+',text)
		if rr:
			return int(rr[0])
		else:
			return 0

def extract_direction_index(text):
	if text.startswith('<<') or text.startswith('«'):
		return -2
	else:
		rr=re.findall('^\d+',text)
		if rr:
			return int(rr[0])
		else:
			return 0