import os

import logging
from enum import IntEnum
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, Job

from oz.handlers import queue_reply, start,help,error,location,msg

from .config import basedir
from .oz_application import app,log_handler

class TelegramHooks:
	class states(IntEnum):
	    location, station_from,trip=range(3)
	    
	def __init__(self):
	    self.LOCATION, STATION_FROM,TRIP,STATION_TO=range(4)
	    self.updater=Updater(app.config['TELEGRAM_TOKEN'])
	    self.setup_logger()
	    self.setup_webhooks()
	    self.setup_handlers()
	    app.logger.info('ozbot: setup ok')

	def setup_logger(self):
	    self.updater.bot.logger.setLevel(logging.DEBUG)
	    self.updater.logger.setLevel(logging.DEBUG)
	    self.updater.dispatcher.logger.setLevel(logging.DEBUG)

	    self.updater.logger.addHandler(log_handler)
	    self.updater.dispatcher.logger.addHandler(log_handler)
	    self.updater.bot.logger.addHandler(log_handler)

	def setup_handlers(self):
	    dp=self.updater.dispatcher
	    dp.add_handler(CommandHandler("start",start))
	    dp.add_handler(CommandHandler("help",help))
	    dp.add_handler(MessageHandler([Filters.location], location))
	    dp.add_handler(MessageHandler([Filters.text], msg))
	    dp.add_error_handler(error)

	    queue_job = Job(queue_reply, 0.035)
	    self.updater.job_queue.put(queue_job)



	def setup_webhooks(self):
	    self.updater.start_webhook(listen='0.0.0.0',
	                          port=443,
	                          cert=app.config['CERT_PATH'], 
	                          key=app.config['KEY_PATH'], 
	                          url_path='/ozbot/{0:s}'.format(app.config['TELEGRAM_TOKEN']),
	                          webhook_url='https://{0:s}:{1:d}/ozbot/{2:s}'.format(app.config['BOT_HOST_IP'], app.config['BOT_PORT'],app.config['TELEGRAM_TOKEN']))


