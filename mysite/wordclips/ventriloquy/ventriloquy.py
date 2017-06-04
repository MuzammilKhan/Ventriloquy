#! /usr/bin/python3
import sys
import errno
import os
from pydub import AudioSegment
import wordclips
from wordclips.models import Wordclip

# def find(name, path):
#     for root, dirs, files in os.walk(path):
#         if name in files:
#             return os.path.join(root, name)

class Ventriloquy:
	"""
	Main handling audio/video generation

	"""
	def __init__(self):
		pass


	def check_words(self, wl):
		"""
		Check if the given list of word can all be found in the database

		Parameters
		----------
			wl -- a list of words


		Return
		----------
			err   -- error code
			         0 - no error
					 -1 - something wrong
			clips -- return a list of objects representing the clips, which contains
			         the path and the speaker of the clip
		"""

		clips = []
		for w in wl:
			try:
				o = Wordclip.objects.get(name=w)
			except Wordclip.DoesNotExist:
				# TODO: more handling code to nonexist item in the DB
				print(w + " is NOT in the database yet.")
				return -1, w
			else:
				print(w + " is in the database.")
				print('path of word ' + w + ' is: ' + o.soundpath)
				clips.append(o)


		# Print out the results
		print('@@@@@@ input word list')
		for c in clips:
			dis = "%s spoken by %s" % (str(c), str(c.speaker))

			print(dis)

		print('@@@@@@')

		return 0, clips


	def create_audio(self, words) :
		"""
		Generating audio from a list of words

		Parameters
		----------
			words -- a list of words (string)

		Return
		----------
			err   -- error code
			         0 - no error
					 -1 - something wrong
			word  -- if every clip can be found, return a empty list, otherwise
			         return the word that is missing

		"""
		err, obj_list = self.check_words(words)
		if err != 0:
			return err, obj_list

		combined_audio = AudioSegment.silent(duration=0)
		audio = AudioSegment.silent(duration=0)
		APP_ROOT = os.path.abspath(os.path.dirname(wordclips.__file__))
		# SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

		for word in words:
			if word == '-': #dashes seperated by space will insert extra silences
				audio = AudioSegment.silent(duration=100)
			else:
				# For now it only word with local folders
				# TODO: graceful fail over
				clip_path = APP_ROOT + "/clips/" + word + "/1.wav"

				# check if the clip exists
				if os.path.isfile(clip_path):
					audio = AudioSegment.from_wav(clip_path)
					combined_audio += audio + AudioSegment.silent(duration=50)
				elif os.path.isfile(APP_ROOT + "/clips/" + word.lower() + "/1.wav"):
					audio = AudioSegment.from_wav(APP_ROOT + "/clips/" + word.lower() + "/1.wav")
					combined_audio += audio + AudioSegment.silent(duration=50)
				else:
					# Find to find the current word in the db
					return -1, word

		combined_audio.export(APP_ROOT + "/../static/they-say.wav", format="wav")
		# success
		return 0, []
