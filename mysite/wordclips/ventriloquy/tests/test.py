#! /usr/bin/python3
import unittest
import sys
sys.path.append("..")
import speech2text
import make_them_say
import ast
import os
import shutil
# from watson_developer_cloud import SpeechToTextV1

class TestSpeech2Text(unittest.TestCase):

	# def is_new_clip_better(word, new_s, new_e, old_s, old_e):
	# 	self.assertEqual()

	def test_get_good_timestamps(self):
		good_timestamps = {}
		offset = 0.0

		# file for true timestamps
		with open("sc/get_good_timestamps.txt", 'r') as file:
			data=file.read()
		true_timestamps = ast.literal_eval(data)

		#file to test get_good_timestamps
		with open("sc/good_timestamps.json") as data_file:
			speech2text.get_good_timestamps(good_timestamps, data_file, offset)
		
		self.assertEqual(good_timestamps, true_timestamps)

	def test_extract_words(self): 
		speech2text.output_folder = "sc/extract_words"
		shutil.rmtree(speech2text.output_folder) #clear workspace and remake it
		os.makedirs(speech2text.output_folder)

		orig_clip = "sc/test_speech.mp4"
		threadID = 0

		with open("sc/extract_words_timestamps.txt", 'r') as file:
			data=file.read()
		good_timestamps = ast.literal_eval(data)

		speech2text.extract_words(orig_clip, good_timestamps, threadID)

		# TODO: maybe run each clip against IBM Bluemix?

		extracted_all = True
		subdirectories = os.listdir(speech2text.output_folder)

		for key, val in good_timestamps.items():
			if key.lower() in subdirectories:
				continue
			else:
				extracted_all = False
				break

		self.assertTrue(extracted_all)


# class TestMakeThemSay(unittest.TestCase):




if __name__ == '__main__':
	unittest.main()