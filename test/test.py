import unittest
import sys
sys.path.append("..")
import speech2text.py
import make_them_say.py


class TestSpeech2Text(unittest.TestCase):

	def setup(self):
		self.assertEqual('setup'.upper(), 'SETUP') #example, delete this 


class TestMakeThemSay(unittest.TestCase):

	def setup(self):
		self.assertEqual('setup'.upper(), 'SETUP') #example, delete this 



if __name__ == '__main__':
	unittest.main()