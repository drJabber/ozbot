#!flask/bin/python3
import logging
import sys

sys.path.insert(0, "/opt/OzElectroBot")
sys.path.insert(0, "/opt/OzElectroBot/oz")
sys.path.insert(0, "/opt/OzElectroBot/flask")
sys.path.insert(0, "/opt/OzElectroBot/flask/lib/python3.5/site-packages")

from oz import OzFramework


#logging.basicConfig(stream=sys.stderr)

#from oz import app as application
oz_fwk=OzFramework()