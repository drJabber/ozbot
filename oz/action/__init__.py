

class Action(object):
	def __init__(self,text,flags):
		self.text=text
		self.flags=flags

	def is_backward(self):
		return self.text.startswith('<<') or self.text.startswith('«')

	def is_forward(self):
		return self.text.endswith('>>')

	def is_last(self):
		return self.text.startswith('>>')
