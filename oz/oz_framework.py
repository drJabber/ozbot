from .oz_application import init_application, app
#from .oz_database import db

from .hooks import TelegramHooks
#from .models import rzd_codes_class

class OzFramework:
    def __init__(self):
    #"
    #initialize flask app
    #initialize telegram bot instance
    #"
        self.tg_hooks=TelegramHooks()
