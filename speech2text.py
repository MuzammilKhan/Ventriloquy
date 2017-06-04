#! /usr/bin/python3
import sys
import os
import glob
import shutil
from pydub import AudioSegment
import json
from watson_developer_cloud import SpeechToTextV1
import conf #contains username and password to access Watson API
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import threading

######################################################################
# global variables
######################################################################

stt = SpeechToTextV1(	#Watson Speech To Text API login info
	username = conf.username, 
	password = conf.password,
	x_watson_learning_opt_out=True
)

#select number of threads
num_threads = 1
#the following will set the number of threads equal to the amount of logical processors on the machine
if sys.platform == 'win32':
	num_threads = ((int)(os.environ['NUMBER_OF_PROCESSORS']))
else:
	num_threads = ((int)(os.popen('grep -c cores /proc/cpuinfo').read()))
print("Using " + str(num_threads) + " threads...")

special_chars = ['<', '>', '\\', '/', '*', ':', '?', '\"', '.'] # used later to detect special characters

basename = ""
person = ""

######################################################################
# classes and functions
######################################################################
class myThread (threading.Thread): #used this as guide: https://www.tutorialspoint.com/python3/python_multithreading.htm
	def __init__(self, threadID, audio, start_time):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.audio = audio
		self.start_time = start_time

	def run(self):
		end_time = len(self.audio)
		increment_by = 60000
		for i in range(self.threadID, end_time, increment_by):
			if(i + 60000 > end_time):
				audio_chunk = self.audio[i:end_time]
			else:
				audio_chunk = self.audio[i:i+60000]
			audio_chunk.export("workspace/" + str(self.threadID) + "_" + str(i) + ".wav", format="wav")

			#Use Watson Speech API on audio chunk
			with open("workspace/" + str(self.threadID) + "_" + str(i) + ".wav", 'rb') as audio:
				stt.models()
				stt.get_model('en-US_BroadbandModel')

				#these parameters above can be altered to effect the output of the api
				stt_result = stt.recognize( audio, content_type='audio/wav', 
													timestamps=True, 
													word_confidence=True, 
													continuous=True, 
													profanity_filter=False,
													word_alternatives_threshold=0.0 )

				#dump response to a json file if we want to check it later then open it
				with open('speech-snippets/' + basename + '_' + str(i) + '.json', 'w') as data_file:
					json.dump(stt_result, data_file, indent=1)
				with open('speech-snippets/' + basename + '_' + str(i) + '.json') as data_file:
					good_timestamps = prune_wrong_recog(None, data_file, float(self.start_time)/1000, self.threadID)

				#clip audio into word clips
				extract_words(sys.argv[2], good_timestamps, i/1000, self.threadID)

def ffmpeg_extract_subclip(filename, start, end, targetname=None):
	"""
	Creates a new video file playing video file "filename" between
		the times "start" and "end". 

	Parameters
	--------------------
		filename			-- 	path
		start 				--	time to start cutting from
		end 				--	time to finish cutting to
		targetname			--	output file name (not used)

	Returns
	--------------------
		nothing
	"""
	""" 
		Note: This function is from the moviepy library but it was buggy so I fixed it here"""
	name,ext = os.path.splitext(filename)
	if not targetname:
		T1, T2 = [int(1000*t) for t in [start, end]]
		targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)
	
	cmd = [get_setting("FFMPEG_BINARY"), "-y",
	  "-i", filename,
	  "-ss", "%0.2f"%start,
	  "-t", "%0.2f"%(end-start),
	  targetname]
	
	subprocess_call(cmd, False)

def prune_wrong_recog( script, data_file, offset, ID ):
	"""
	Returns the correctly recognized words and their timestamps.

	Parameters
	--------------------
		script			-- 	Array of transcript of a speech. This is assumed to be completely correct.
		datafile		-- 	JSON file of Watson's generated text, containing 
						word guesses, start and end times, confidence levels, etc.
						This will most likely have some incorrect speech-to-text translations.
		offset			-- The amount by which we change the timestamp

	Returns
	--------------------
		good_timestamps	--	dict of words to timestamps, of format: 
						(word, (start_time, end_time)) --> (string, (int, int)) 
						These will be completely accurate.
	"""

	good_timestamps = []
	data = json.load(data_file)

	for res in data['results']:
		for word_alternatives in res['word_alternatives']:
			word = word_alternatives['alternatives'][0]
			if word['confidence'] > 0.95:
				start_time = word_alternatives['start_time'] + offset
				end_time = word_alternatives['end_time'] + offset
				pred_word = word['word']
				tup = (pred_word, start_time, end_time) 
				good_timestamps.append(tup)

	return good_timestamps

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
	dir = os.path.dirname(path)
	if not os.path.exists(dir):
		os.makedirs(dir)

def extract_words(orig_clip, good_timestamps, seconds, ID):
	"""
	Extract word clips from the input audio clip.

	Parameters
	--------------------
		orig_clip			-- 	The input audio clip that we want to extract word clips from
		good_timestamps		-- 	The timestamps of the words
		seconds				--  How many seconds have passed

	Returns
	--------------------
		nothing 
	"""
	for cur, nxt in zip(good_timestamps, good_timestamps[1:]+[(None, float("inf"), None)]):
		word = cur[0]
		start =  seconds + cur[1]
		end =  seconds + cur[2]
		nxt_start =  seconds + nxt[1]
		
		#check for special chars b/c windows doesn't allow these in filenames
		no_special_char = True
		for char in special_chars:
			if char in word:
				no_special_char = False
				break

		if no_special_char:
			path = "clips/" + person + "/" + word.lower() + "/" + "thread" + str(ID) + "_"
			assure_path_exists(path)
			num_clips = len(glob.glob(path + "*")) # get num of clips already in folder, to avoid overwiting
			ffmpeg_extract_subclip(orig_clip, start, end, targetname=(path + str(num_clips + 1) + ".mp4"))

######################################################################
# main
######################################################################

def main(argv) :
	if(len(sys.argv) != 3): #TODO: change this to allow input transcript
		print('Usage: speech2text.py person inputfile')
		sys.exit(2)

	#modifying global variables
	global basename
	global person
	global clip_len

	#open input file and convert to flac (assume  test file in same directory for now)
	basename = os.path.splitext(os.path.basename(sys.argv[2]))[0]
	file_ext = os.path.splitext(sys.argv[2])[1][1:]
	audio_init = AudioSegment.from_file(sys.argv[2], file_ext) #assuming input files are all supported by ffmpeg
	audio_chunk = AudioSegment.silent(duration=0) 
	end_time = len(audio_init)
	person = sys.argv[1].lower()

	if os.path.exists("workspace"):
		shutil.rmtree("workspace") #clear workspace and remake it
		os.makedirs("workspace")
	else:
		os.makedirs("workspace")

	clip_len = end_time / num_threads
	threads = []
	start_time = 0
	end = 0

	for i in range(0,num_threads): 
		start_time = i * clip_len
		end = end_time if (i == num_threads -1) else (i+1) * clip_len -1

		audio_chunk = audio_init[start_time: end]
		thread = myThread(i, audio_chunk, start_time)
		thread.start()
		threads.append(thread)

	for t in threads:
		t.join()

	path = "clips/" + "obama" + "/"
	subdirectories = os.listdir(path)
	for subdir in subdirectories:
		if not '.' in subdir:
			files = os.listdir(path + subdir)
			maximum = 0
			biggest_file_path = ""
			for file in files:
				path_to_file = path + subdir + "/" + file
				if maximum < len(file):
					maximum = len(file)
					biggest_file_path = path_to_file
				else:
					os.remove(path + subdir + "/" + file)
			os.rename(biggest_file_path, path + subdir + "/1.mp4")

if __name__ == "__main__" :
	main(sys.argv[1:])