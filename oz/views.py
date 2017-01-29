from __future__ import unicode_literals
import telegram
import json
import codecs
from app import app
from config import TELEGRAM_TOKEN, CERT_PATH
from flask import request


global bot
bot=telegram.Bot(token=TELEGRAM_TOKEN)
app.logger.info('ozbot views')

@app.route('/%s' % (TELEGRAM_TOKEN),methods=['GET', 'POST'])
def hello():
    app.logger.info('ozbot: hello')
    if request.method=='POST':
        app.logger.info('ozbot: before load request data')
        reader=codecs.getreader('UTF-8')
        message = json.load(reader(request.stream))
        app.logger.info('ozbot: after load request data')
        if message['message']['text'] == '/ping':
            bot.send_message(message['message']['chat']['id'], 'Pong!')
    return 'ok'


