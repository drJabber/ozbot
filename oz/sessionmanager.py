import os
import glob
import pickle
import random
import config
import logging
from oz_application import app
from session import Session
from action import Action

def get_fname(sid):
	return os.path.join(app.config['USERS_PATH'],'{0}.usr'.format(sid))

def save_session(session):
	if session is None:
		return
		
	with open(get_fname(session.sid), 'wb') as outfile:
		pickle.dump(session, outfile)

def get_session(sid):
	if os.path.exists(get_fname(sid)):
		session = None

		with open(get_fname(sid), 'rb') as outfile:
			session = pickle.load(outfile)

		return session
	else:
		return None

def new_session(sid, nickname=None, reply=lambda *x, **y: None):
	s = Session(sid)

	if nickname is None:
		nickname='(None)'

	s.user_nickname = nickname

	text=nickname+', для выяснения, какие станции находятся поблизости мне необходимы твои координаты'

	s.state='location'
	reply(text, s.get_actions())

	save_session(s)

def show_source_stations(sid, location=None, reply=lambda *x, **y: None):
	s = get_session(sid)
	if s is None:
		s = Session(sid)

	s.initialize()
	show_source_stations_page(s, location,reply)



def show_source_stations_page(session, location,reply):
	actions=session.get_source_stations(location)
	if actions[0].text.startswith('>>'):
		text=session.user_nickname+', в радиусе 3 км нет ж/д станций. Ты можешь попытаться передать свои координаты еще раз'
		session.initialize()
	else:
		text=session.user_nickname+', выбери станцию отправления'
		session.state='source'

	reply(text, actions)

	save_session(session)

def show_source_directions(session, source_idx, reply):
	session.source_station=source_idx
	station=session.source_stations[source_idx]
	actions=station.get_direction_actions()
#	reply('trace: state={2:s}, station={0:s}, direction={1:0}'.format(station.yandex_name,station.direction, session.state))
	if len(actions)>0:
		text=session.user_nickname+', выбери направление'
		session.state='direction'
		reply(text, actions)
		save_session(session)
	else:
		show_source_direction_schedule(session,-1,reply)


def show_source_direction_schedule(session,direction_idx,reply):
	station=session.source_stations[session.source_station]
	station.direction=direction_idx
	show_schedule_page(session,reply)

def show_schedule_page(session,reply):
	station=session.source_stations[session.source_station]
	actions=station.get_schedule_actions()

#	reply('trace: state={2:s}, station={0:s}, direction={1:0}'.format(station.yandex_name,station.direction, session.state))
	direction=station.direction
	if direction:
		msg_part=station.directions[direction]
	else:
		msg_part='со станции {0:s} '.format(station.yandex_name)

	if actions[0].text.startswith('>>') or actions[0].text.startswith('<<'):
		text=session.user_nickname+', в ближайшие сутки '+msg_part+' нет электричек. Попробуйте выбрать другое направление, либо другую станцию отправления.'
	else:
		text=session.user_nickname+', вот расписание электричек '+msg_part+'. Ты можещь выбрать электричку, чтобы узнать остановки'

	session.state='schedule'
	reply(text, actions)

	save_session(session)


def show_thread_stops(session, schedule_idx, reply):
	station=session.source_stations[session.source_station]
	station.schedule_index=schedule_idx
	show_thread_stops_page(session,reply)

def show_thread_stops_page(session, reply):
	station=session.source_stations[session.source_station]
	sh_item=station.schedule[station.schedule_index]
	actions=sh_item.get_stop_actions(station)
	text='{0:s}, вот оcтановки электрички {1:%d.%m.%Y %H:%M} {2:s}'.format(session.user_nickname, sh_item.arrival,sh_item.destination_title)

	session.state='thread'
	reply(text,actions)
	save_session(session)

def show_trip_message(session, stop_idx, reply):
	station=session.source_stations[session.source_station]
	sh_item=station.schedule[station.schedule_index]
	sh_item.stop_index=stop_idx
	stop=sh_item.stops[stop_idx]

	dtt1=sh_item.arrival
	if dtt1==None:
		dtt1=sh_item.departure

	dtt2=stop.arrival
	if dtt2==None:
		dtt2=stop.departure

	text='{0:s}, итак: {1:%d.%m.%Y в %H:%M} ты отправляешься со станции {2:s} и прибываешь {3:%d.%m.%Y в %H:%M} на станцию {4:s}\n\nСтанция отправления тут:'.format(session.user_nickname, dtt1, station.yandex_name,dtt2,stop.title)

	location={"latitude":station.latitude, "longitude":station.longitude,"title":"станция отправления","address":station.yandex_name}
	reply(text,[],location)



def message(sid, reply, text):
	s = get_session(sid)
	if not s:
		reply('Что-то не срослось. Попробуй /start')
	elif s.message(reply, text):
		s=Session(sid)

	save_session(s)

