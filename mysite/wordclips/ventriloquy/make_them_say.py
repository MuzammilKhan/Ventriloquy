#! /usr/bin/python3
import sys
import os
import shutil
import moviepy.editor as mp
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
from pydub import AudioSegment

clips_path = ""
output_folder = ""

def assure_path_exists(path):
	"""
	Check if path exists. If not, create it.

	Parameters
	--------------------
		path			-- 	path

	Returns
	--------------------
		nothing
	"""
	if not os.path.exists(path):
		os.makedirs(path)

def concat(person, clips):
	"""
	Concatenates the the input clips into an output video for a given person
	Parameters
	--------------------
		clips			-- 	Array of clip names excluding filetype as we assume them to be .mp4

	Returns
	--------------------
		returns nothing but creates an output video
	"""

	#create workspace for less clutter
	if os.path.exists("workspacets"):
		shutil.rmtree("workspacets") #clear workspace and remake it
		os.makedirs("workspacets")
	else:
		os.makedirs("workspacets")

	#ffmpeg setup and calls
	concat_param = "concat:"
	first = True
	for clip in clips:
		cmd = [get_setting("FFMPEG_BINARY"), "-y",
			"-i", clips_path + "/" + person + "/" + clip + "/1.mp4",
			"-c", "copy", "-bsf:v",  "h264_mp4toannexb",
			"-f", "mpegts",
			"workspacets/" + clip + ".ts"]

		try:
			subprocess_call(cmd, False, False)
		except:
			print ("Oops! " + person.title() + " doesn't know the word '" + clip + "'")
			return clip

		if first:
			concat_param = concat_param + "workspacets/" + clip + ".ts"
			first = False
		else:
			concat_param = concat_param + "|" + "workspacets/" + clip + ".ts"

	fcmd = [get_setting("FFMPEG_BINARY"), "-y",
	  "-i", concat_param,
	  "-c", "copy",
	  "-bsf:a", "aac_adtstoasc",
	  output_folder + "/tmp.mp4"]

	subprocess_call(fcmd, False)
	return ""

def normalize(clip):
	"""
	Normalizes the audio of the the input clip into an output video
	Parameters
	--------------------
		clips			-- 	Array of clip names excluding filetype as we assume them to be .mp4

	Returns
	--------------------
		returns nothing but creates an output video
	"""

	cmd = ["ffmpeg-normalize", "-fu",
	  "--format", "mp4",
	  clip]

	subprocess_call(cmd, False)
	if os.path.exists(output_folder + "/they-say.mp4"):
		os.remove(output_folder + "/they-say.mp4")
	os.rename(output_folder + "/normalized-tmp.mp4", output_folder + "/they-say.mp4")
	os.remove(output_folder + "/tmp.mp4")

def run(argv):
	if(len(argv) != 4):
		print('Usage: make-them-say.py clips_path output_folder person statement')
		sys.exit(len(argv))

	global clips_path
	global output_folder

	clips_path = argv[0]
	output_folder = argv[1]

	assure_path_exists(clips_path)
	assure_path_exists(output_folder)

	phrase = os.path.splitext(argv[3])[0]
	words = phrase.split()

	rtn = concat(argv[2].lower(), words)
	if rtn == "":
		normalize(output_folder + "/tmp.mp4")
		audio = AudioSegment.from_file(output_folder + "/they-say.mp4", "mp4")
		audio.export(output_folder + "/they-say.wav", "wav")
	return rtn

def main(argv) :
	run(argv)

if __name__ == "__main__" :
	main(sys.argv[1:])
