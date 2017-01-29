import os

basedir=os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['DB_URL']
    DB_SERVICE=os.environ['DB_SERVICE']
    CERT_PATH='/etc/ssl/certs/my.pem'
    KEY_PATH='/etc/ssl/private/my.key'
    TELEGRAM_TOKEN='XXXXXXXXXXX:YYYYYYYYYYYYYYY' #telegram API token
    YANDEX_TOKEN='xxxxxxxx-yyyy-????' #rasp.yandex.ru API token
    LOG_DIR=os.path.join(basedir,'tmp')
    LOG_FILE='ozbot.log'
    LOG_FORMAT='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    USERS_PATH=os.path.join(basedir,'usr')
    BOT_HOST_IP='my.domain.com' #host IP or domain name
    BOT_PORT=8443 #service port

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

