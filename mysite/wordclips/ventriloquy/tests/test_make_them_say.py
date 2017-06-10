#! /usr/bin/python3
import unittest
import sys
import ast
import os
import shutil
from pydub import AudioSegment

sys.path.append("..")
import speech2text
import make_them_say

class TestMakeThemSay(unittest.TestCase):

	def test_assure_path_exists(self):
		path = "bad"
		if os.path.exists(path):
			os.rmdir(path)
		self.assertFalse(os.path.exists(path))
		make_them_say.assure_path_exists(path)
		self.assertTrue(os.path.exists(path))
		os.rmdir(path)

	def test_run(self):
		person = "trump"
		words = "people really like really like vandalism"
		clips_path = "testing_clips"
		output_folder = "testing_outputs"
		make_them_say.run([clips_path, output_folder, person, words])

		s2p_input = "testing_outputs/they-say.mp4"
		s2p_output = "testing_outputs/clips"
		speech2text.run([s2p_output, person, s2p_input])

		self.assertTrue(os.path.exists(s2p_output + "/" + person + "/people/1.mp4"))
		self.assertTrue(os.path.exists(s2p_output +  "/" + person + "/really/1.mp4"))
		self.assertTrue(os.path.exists(s2p_output +  "/" + person + "/like/1.mp4"))
		self.assertTrue(os.path.exists(s2p_output +  "/" + person + "/vandalism/1.mp4"))

if __name__ == '__main__':
	unittest.main()