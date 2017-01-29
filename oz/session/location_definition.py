import constants
from action import Action

def get_location_actions(self):
	actions=[ Action('Отправьте ваше местоположение, чтобы получить список ближайших станций',{constants.ACTION_FLAG_REQUEST_LOCATION})]
	return actions


