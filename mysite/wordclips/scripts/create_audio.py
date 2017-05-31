#! /usr/bin/python3
import sys
import errno
import os
from pydub import AudioSegment
import wordclips

# def find(name, path):
#     for root, dirs, files in os.walk(path):
#         if name in files:
#             return os.path.join(root, name)

def create_audio(words) :

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
			elif os.path.isfile(APP_ROOT + "/clips" + word.lower() + "/1.wav"):
				audio = AudioSegment.from_wav(APP_ROOT + "/clips" + word.lower() + "/1.wav")
				combined_audio += audio + AudioSegment.silent(duration=50)
			else:
				# Find to find the current word in the db
				return -1, word

	combined_audio.export(APP_ROOT + "/../static/they-say.wav", format="wav")
	# success
	return 0, []
