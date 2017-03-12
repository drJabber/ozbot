import os
import glob
import pickle
import random
import config
import logging
from oz_application import app
from session import Session
from action import Action
from oz.utils import telegram_trace

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


def show_help(sid, nickname=None, reply=lambda *x, **y: None):
	s = get_session(sid)

	if nickname is None:
		nickname='(None)'

	s.user_nickname = nickname

	reply(nickname+', вот что можно делать с этим ботом:')
	reply('\tКоманда /start - начинает сеанс бота')
	reply('\tДалее следует передать боту твое местоположение -для поиска ближайших станций')
	reply('\tПосле передачи местоположения возможно 2 сценария работы.')
	reply('\t1. Выбрав на клавиатуре станцию отправления, можно узнать расписание электричек по этой станции и время прибытия в пункт назначения')
	reply('\t2. Передав боту название станции назначения, можно получить расписание электричек от ближайших станций до станции назначения')

	save_session(s)

def process_location(sid, location=None, reply=lambda *x, **y: None):
	s = get_session(sid)
	if s is None:
		s = Session(sid)

	s.initialize('location')
	show_source_stations_page(s, location,reply)

def show_source_stations_page(session, location,reply):
	actions=session.get_source_stations(location)
	if actions[0].is_last():
		text=session.user_nickname+', в радиусе 3 км нет ж/д станций. Ты можешь попытаться передать свои координаты еще раз'
		session.initialize('location')
	else:
		if session.custom_destination>=0:
			text='Хорошо, {0:s}, едем на станцию *"{1:s}"*. Теперь выбери станцию отправления. Можешь также снова отправить название станции назначения'.format(session.user_nickname,session.get_custom_destination_name())
			session.set_state('source')
		else:
			text=session.user_nickname+', выбери станцию отправления или отправь название станции назначения'
			session.set_state('source')

	reply(text, actions)

	save_session(session)

def show_custom_destinations(session, reply, text):
	if len(text)>=3:
		session.custom_destination_pattern=text.upper()
		session.custom_destination=-1;
		session.custom_destination_page=0;
		show_custom_destinations_page(session,reply)
	else:
		reply(session.user_nickname+', ты указал слишком короткое название станции отправления. Попробуй что-нибудь подлиннее.')

def show_custom_destinations_page(session, reply):
	actions=session.get_custom_destination_actions()

	if actions[0].is_last():
		text=session.user_nickname+', я не нашел станций, названия которых начинаются или похожи на *"{0:s}"*'.format(session.custom_destination_pattern)
		show_last_state(session,reply)
	else:
		suffix=''
		if session.state=='source':
			suffix=', затем выбери станцию отправления'
		text=session.user_nickname+', вот станции, название которых начинаются на *"{0:s}"*, выбери станцию {1:s}'.format(session.custom_destination_pattern,suffix)

		session.state='custom_destination'
		reply(text, actions)
		save_session(session)

def show_custom_schedule(session,reply):
	session.custom_schedule_page=0
	show_custom_schedule_page(session,reply)

def show_custom_schedule_page(session,reply):

	actions=session.get_custom_schedule_actions()

	station=session.get_source_station()
	custom_destination_name=session.get_custom_destination_name()
	msg_part1='от станции *"{0:s}"* до станции *"{1:s}"*'.format(station.yandex_name,custom_destination_name)
	msg_part2='до станции *"{0:s}"*'.format(custom_destination_name)

	if actions[0].is_last() or actions[0].is_backward():
		text=session.user_nickname+', в ближайшие сутки '+msg_part1+' нет электричек. Попробуйте другую станцию назначения или отправления. Можно также попытаться отправить свои координаты еще раз.'
	else:
		text=session.user_nickname+', вот расписание электричек '+msg_part2+'. Ты можешь выбрать электричку, чтобы узнать остановки'

	session.state='custom_schedule'
	reply(text, actions)
	save_session(session)



def show_last_state(session,reply):
	session.custom_destination=-1;
	session.custom_destination_page=0;
	session.restore_state(reply)
	save_session(session)


def show_source_directions(session, source_idx, reply):
	session.source_station=source_idx

	if session.custom_destination>=0:
		show_custom_schedule(session,reply)
	else:
		actions=session.get_source_station().get_direction_actions()
		if len(actions)>0:
			text=session.user_nickname+', выбери направление'
			session.set_state('direction')
			reply(text, actions)
			save_session(session)
		else:
			show_source_direction_schedule(session,-1,reply)


def show_source_direction_schedule(session,direction_idx,reply):
	station=session.get_source_station()
	station.direction=direction_idx
	show_schedule_page(session,reply)

def show_schedule_page(session,reply):
	station=session.source_stations[session.source_station]
	actions=station.get_schedule_actions()

	direction=station.direction
	if direction:
		msg_part=station.directions[direction]
	else:
		msg_part='со станции *"{0:s}"* '.format(station.yandex_name)

	if actions[0].is_last() or actions[0].is_backward():
		text=session.user_nickname+', в ближайшие сутки '+msg_part+' нет электричек. Попробуйте выбрать другое направление, либо другую станцию отправления.'
	else:
		text=session.user_nickname+', вот расписание электричек '+msg_part+'. Ты можешь выбрать электричку, чтобы узнать остановки'

	session.set_state('schedule')
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
	text='{0:s}, вот оcтановки электрички {1:%d.%m.%Y %H:%M} *{2:s}*'.format(session.user_nickname, sh_item.arrival,sh_item.destination_title)

	session.set_state('thread')
	reply(text,actions)
	save_session(session)

def show_trip_message(session, stop_idx, reply):
	station=session.get_source_station()
	sh_item=station.schedule[station.schedule_index]

	sh_item.stop_index=stop_idx
	stop=sh_item.stops[stop_idx]

	dtt1=sh_item.arrival
	if dtt1==None:
		dtt1=sh_item.departure

	dtt2=stop.arrival
	if dtt2==None:
		dtt2=stop.departure

	text='{0:s}, итак: *{1:%d.%m.%Y в %H:%M}* ты отправляешься со станции *{2:s}* и прибываешь *{3:%d.%m.%Y в %H:%M}* на станцию *{4:s}*\n\nСтанция отправления тут:'.format(session.user_nickname, dtt1, station.yandex_name,dtt2,stop.title)

	location={"latitude":station.latitude, "longitude":station.longitude,"title":"станция отправления","address":station.yandex_name}
	reply(text,[],location)

def show_custom_info(session,reply):
	sh_item=session.get_custom_schedule_item()

	text='Итак, твой поезд отправляется от станции *"{0:s}"* {1:%d.%m.%Y в %H:%M} и прибывает на станцию *"{2:s}"* {3:%d.%m.%Y в %H:%M}.\nСчастливого пути, {4:s}!\n\nPS. Станция отправления тут:'.format(sh_item.from_title, sh_item.departure, sh_item.to_title,sh_item.arrival,session.user_nickname)

	station=session.get_source_station()
	location={"latitude":station.latitude, "longitude":station.longitude,"title":"станция отправления","address":station.yandex_name}

	reply(text,[],location)



def message(sid, reply, text):
	s = get_session(sid)
	if not s:
		reply('Что-то не срослось. Попробуй /start')
	elif s.message(reply, text):
		s=Session(sid)

	save_session(s)

