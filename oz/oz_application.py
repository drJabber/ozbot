import os
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import config

def init_application():
    app = Flask('oz')
    app.debug=True
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    app.logger.setLevel(logging.DEBUG)

    log_handler=RotatingFileHandler(os.path.join(app.config['LOG_DIR'],app.config['LOG_FILE']),'a',1*1024*1024,10)
    log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    log_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(log_handler)

    return app,log_handler

(app,log_handler)=init_application()