import constants
from action import Action

def get_location_actions(self):
	if self.state=='location':
		actions=[ Action('Отправьте ваше местоположение, чтобы получить список ближайших станций',{constants.ACTION_FLAG_REQUEST_LOCATION})]
	elif self.state=='location_goto':
		actions=[ Action('Отправьте ваше местоположение, чтобы получить расписание электричек до станции {0:s}'.format(self.target),{constants.ACTION_FLAG_REQUEST_LOCATION})]
	return actions


def location_not_selected(session, reply, text):
	reply(session.user_nickname+', сначала необходимо передать твое местоположение')