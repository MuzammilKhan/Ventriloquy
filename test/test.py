import unittest
import ../speech2text.py
import ../make-them-say.py


class TestSpeech2Text(unittest.TestCase):

	def setup(self):
		self.assertEqual('setup'.upper(), 'SETUP') #example, delete this 


class TestMakeThemSay(unittest.TestCase):

	def setup(self):
		self.assertEqual('setup'.upper(), 'SETUP') #example, delete this 



if __name__ == '__main__':
	unittest.main()