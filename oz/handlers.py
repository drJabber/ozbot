import telegram 
from telegram.ext.dispatcher import run_async
from telegram import KeyboardButton, ReplyKeyboardMarkup
from collections import deque

import constants
import sessionmanager

queue=deque([])

def append_button(keyboard, action):
	text=action.text
	flags=action.flags
	request_location=constants.ACTION_FLAG_REQUEST_LOCATION in flags
	request_contacts=constants.ACTION_FLAG_REQUEST_CONTACTS in flags
	btn=telegram.KeyboardButton(text, request_location=request_location, request_contacts=request_contacts)
	keyboard.append([btn])

@run_async
def _reply(c_id, bot, txt, actions=None, location=None, repeat=True):
	bot.logger.info('ozbot: %s' % ('_reply'))
	if c_id == 0:
		return
	if actions:
		custom_keyboard = [ ]

		for action in actions:
			append_button(custom_keyboard,action)

		bot.logger.info('ozbot: %s' % custom_keyboard)

		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
		try:
			if len(custom_keyboard)>0:
				bot.sendMessage(c_id, text=txt, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
			else:
				bot.sendMessage(c_id, text=txt)

		except Exception as e:
			if not repeat:
				raise e

			if '429' in str(e):
				send_job = Job(reply_job, 1, repeat=False, context=(c_id, bot, txt, actions))
				updater.job_queue.put(send_job)
			else:
				raise e

	elif len(txt) > 0:
		bot.sendMessage(c_id, text=txt, parse_mode=telegram.ParseMode.MARKDOWN)

	if location:
		bot.sendVenue(c_id,location["latitude"],location["longitude"],location["title"],location["address"])


def queue_reply(bot, job):
	try:
		message = queue.popleft()

		if message:
			c_id, bot, txt, actions, location, repeat = message
			if location:
				bot.logger.info('ozbot: %s' % ('_reply - location'))
			_reply(c_id, bot, txt, actions, location, repeat)

	except:
		pass


def reply(c_id, bot, txt, actions=None, location=None, repeat=True):
	if c_id == 0:
		return

	queue.append([ c_id, bot, txt, actions, location, repeat ])


def start(bot, update):
	c_id = update.message.chat_id
	global msg,actions
	msg = ''
	actions = None

	bot.logger.info('ozbot: %s' % ('start'))
	def rep(txt, actns=None):
		global msg, actions

		if len(msg) + len(txt) + 2 >= 4096:
			reply(c_id, bot, msg, actions)

			msg = ''
			actions = None


		msg += '\n\n'
		msg += txt

		if actns:
			actions = actns

	username = ''
	try:
		username = bot.getChat(c_id)['username']
	except:
		pass

	sessionmanager.new_session(c_id, username if len(username) > 0 else None, rep)
	if len(msg) > 0 :
		reply(c_id, bot, msg, actions)

def help(bot, update):
	c_id = update.message.chat_id
	global msg,actions
	msg = ''
	actions = None

	bot.logger.info('ozbot: %s' % ('help'))
	def rep(txt, actns=None):
		global msg, actions

		if len(msg) + len(txt) + 2 >= 4096:
			reply(c_id, bot, msg, actions)

			msg = ''
			actions = None


		msg += '\n\n'
		msg += txt

		if actns:
			actions = actns

	username = ''
	try:
		username = bot.getChat(c_id)['username']
	except:
		pass

	sessionmanager.show_help(c_id, username if len(username) > 0 else None, rep)
	if len(msg) > 0 :
		reply(c_id, bot, msg, actions)

def location(bot,update):
	c_id = update.message.chat_id
	global msg, actions
	msg = ''
	actions = None
	bot.logger.info('ozbot: location: latitude: {0:0.4f} , longitude: {1:0.4f}'.format(update.message.location.latitude, update.message.location.longitude))

	def rep(txt, actns=None):
		global msg, actions

		if len(msg) + len(txt) + 2 >= 4096:
			reply(c_id, bot, msg, actions)

			msg = ''
			actions = None


		msg += '\n\n'
		msg += txt

		if actns:
			actions = actns

	sessionmanager.process_location(c_id, update.message.location, rep)
	if len(msg) > 0 :
		reply(c_id, bot, msg, actions)


def msg(bot, update):
	c_id = update.message.chat_id
	global msg, actions, location
	msg = ''

	actions = None
	location=None

	bot.logger.info('ozbot: msg')
	def rep(txt, actns=None, loc=None):
		global msg, actions, location

		if len(msg) + len(txt) + 2 >= 4096:
			reply(c_id, bot, msg, actions,location)

			msg = ''
			actions = None


		msg += '\n\n'
		msg += txt

		if actns:
			actions = actns
		if loc:
			location=loc

	username = ''
	try:
		username = bot.getChat(c_id)['username']
	except:
		pass

	sessionmanager.message(c_id, rep, update.message.text.strip())
	if len(msg) > 0 :
		reply(c_id, bot, msg, actions,location)


def error(bot, update, error):
	bot.logger.warn('Ошибка: %s (%s)' % (update, error))


