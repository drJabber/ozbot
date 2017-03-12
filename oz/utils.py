from oz_application import app

def telegram_trace(reply,text):
	if app.config['DEBUG']:
		reply(text.replace('_','-'))