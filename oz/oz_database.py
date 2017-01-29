from flask_sqlalchemy import SQLAlchemy
from .oz_application import app

db=SQLAlchemy(app)

from .models import rzd_codes_class


