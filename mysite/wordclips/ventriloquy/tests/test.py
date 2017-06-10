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

# from watson_developer_cloud import SpeechToTextV1

class TestSpeech2Text(unittest.TestCase):

	# def is_new_clip_better(word, new_s, new_e, old_s, old_e):
	# 	self.assertEqual()

	def test_assure_path_exists(self):
		# these paths should already exist
		paths = ['sc/', 'sc/extract_words/', 'sc/thread_run/', 'speech-snippets/', 'workspace/']
		for path in paths:
			speech2text.assure_path_exists(path)
			self.assertTrue(os.path.exists(os.path.dirname(path)))

		# what about for folders that don't exist? 
		path = 'nonexistent_path/'
		self.assertFalse(os.path.exists(os.path.dirname(path)))
		speech2text.assure_path_exists(path)
		self.assertTrue(os.path.exists(os.path.dirname(path)))
		os.rmdir('nonexistent_path/')

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

		extracted_all = True
		subdirectories = os.listdir(speech2text.output_folder)

		for key, val in good_timestamps.items():
			if key.lower() in subdirectories:
				continue
			else:
				extracted_all = False
				break

		self.assertTrue(extracted_all)

	def test_thread_run(self):
		sys.stdout = open(os.devnull, 'w')

		speech2text.output_folder = "sc/thread_run"
		speech2text.input_file = "sc/test_speech.mp4"
		audio = AudioSegment.from_file(speech2text.input_file, "mp4")
		thread = speech2text.myThread(0, audio, 0)
		thread.start()
		thread.join()

		with open("sc/extract_words_timestamps.txt", 'r') as file:
			data = file.read()
		true_timestamps = ast.literal_eval(data)

		extracted_all = True
		subdirectories = os.listdir(speech2text.output_folder)

		for key, val in true_timestamps.items():
			if key.lower() in subdirectories:
				continue
			else:
				extracted_all = False
				break
		sys.stdout = sys.__stdout__

		self.assertTrue(extracted_all)


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