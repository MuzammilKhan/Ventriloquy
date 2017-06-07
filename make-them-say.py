#! /usr/bin/python3
import sys
import os
import shutil
import moviepy.editor as mp
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
from pydub import AudioSegment

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
			"-i", "clips/" + person + "/" + clip + "/1.mp4",
			"-c", "copy", "-bsf:v",  "h264_mp4toannexb",
			"-f", "mpegts", 
			"workspacets/" + clip + ".ts"]   

		try:
			subprocess_call(cmd, False, False)
		except:
			print("Oops! Obama doesn't know the word: " + clip + " :(")
			sys.exit()
		
		if first:
			concat_param = concat_param + "workspacets/" + clip + ".ts"
			first = False
		else:
			concat_param = concat_param + "|" + "workspacets/" + clip + ".ts"
  
	fcmd = [get_setting("FFMPEG_BINARY"), "-y",
	  "-i", concat_param,
	  "-c", "copy",
	  "-bsf:a", "aac_adtstoasc",
	  "output/they-say.mp4"]
	
	subprocess_call(fcmd, False)

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
	  "--no-prefix",
	  clip]   

	subprocess_call(cmd, False)

def main(argv) :
	if(len(sys.argv) != 3): 
		print('Usage: make-them-say.py person statement')
		sys.exit(2)

	phrase = os.path.splitext(sys.argv[2])[0]
	words = phrase.split()

	concat(sys.argv[1].lower(), words)
	#normalize("output/they-say.mp4")
	audio = AudioSegment.from_file("output/they-say.mp4", "mp4") 
	audio.export("output/they-say.wav", format="wav")

	
if __name__ == "__main__" :
	main(sys.argv[1:])