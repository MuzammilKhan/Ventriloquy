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
import time

######################################################################
# global variables
######################################################################

stt = SpeechToTextV1(	#Watson Speech To Text API login info
	username = conf.username,
	password = conf.password,
	x_watson_learning_opt_out=True
)

num_threads = 0 # will be set dynamically by detectCPUs()
special_chars = ['<', '>', '\\', '/', '*', ':', '?', '\"', '.'] # used later to detect special characters
basename = ""
person = ""

######################################################################
# classes and functions
######################################################################

def detectCPUs():
	"""
	Detects the number of CPUs on a system. Credit: https://github.com/nunoplopes/alive/blob/master/tests/lit/lit/util.py
	"""
	if hasattr(os, "sysconf"):	# Linux, Unix and MacOS:
		if "SC_NPROCESSORS_ONLN" in os.sysconf_names:	# Linux & Unix:
			ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
			if isinstance(ncpus, int) and ncpus > 0:
				return ncpus
		else: # OSX:
			return int(capture(['sysctl', '-n', 'hw.ncpu']))
	if "NUMBER_OF_PROCESSORS" in os.environ:	# Windows:
		ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
		if ncpus > 0:
			return ncpus
	return 1 # Default

class myThread (threading.Thread): #used this as guide: https://www.tutorialspoint.com/python3/python_multithreading.htm
	def __init__(self, threadID, audio, start_time):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.audio = audio
		self.start_time = start_time

	def run(self):
		audio_len = len(self.audio)
		increment_by = 60000
		good_timestamps = {}

		for i in range(self.threadID, audio_len, increment_by):
			end_time = audio_len if(i + 60000 > audio_len) else i+60000
			audio_chunk = self.audio[i:end_time]

			start = str("%d" % (float(self.threadID*audio_len + i) / 1000))
			end = str("%d" % (float(self.threadID*audio_len + end_time) / 1000))

			path = "workspace/" + basename + "_" + start + "-" + end + ".wav"
			audio_chunk.export(path, format="wav")

		for j in range(self.threadID, audio_len, increment_by):
			t2 = time.time()
			end_time = audio_len if(j + 60000 > audio_len) else j+60000
			start = str("%d" % (float(self.threadID*audio_len + j) / 1000))
			end = str("%d" % (float(self.threadID*audio_len + end_time) / 1000))
			path = "workspace/" + basename + "_" + start + "-" + end + ".wav"

			#Use Watson Speech API on audio chunk
			with open(path, 'rb') as audio:
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
				with open('speech-snippets/' + basename + "_" + start + "-" + end + '.json', 'w') as data_file:
					json.dump(stt_result, data_file, indent=1)
				with open('speech-snippets/' + basename + "_" + start + "-" + end + '.json') as data_file:
					get_good_timestamps(good_timestamps, data_file, float(self.threadID*audio_len + j) / 1000)

				t3 = time.time()
				print("thread " + str(self.threadID) + ", j: " + str(j) + ", time: " + str(t3-t2))

		t4 = time.time()
		print("thread " + str(self.threadID) + " starting to extract_words")
		#clip audio into word clips
		extract_words(sys.argv[2], good_timestamps, 0, self.threadID)
		t5 = time.time()
		print("thread " + str(self.threadID) + " finished extract_words. time: " + str(t5-t4))

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
		Note: This function is from the moviepy library but it was buggy so we fixed it here"""
	name,ext = os.path.splitext(filename)
	if not targetname:
		T1, T2 = [int(1000*t) for t in [start, end]]
		targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)

	cmd = [get_setting("FFMPEG_BINARY"), "-y",
		"-ss", "%0.2f"%start,
	  	"-t", "%0.2f"%(end-start),
	  	"-i", filename,
		"-c:v", "libx264", "-x264opts", "keyint=1:min-keyint=1:scenecut=-1",
	  	targetname]

	subprocess_call(cmd, False)

def is_new_clip_better(word, new_s, new_e, old_s, old_e):
	"""
	Compares two clips, seeing which one is better.
	For now, this function simply considers "better" to be "longer"

	Parameters
	--------------------
		word				-- word being compared
		new_s				-- start time of new word
		new_e 				-- end time of new word
		old_s 				-- start time of old word
		old_e 				-- end time of old word

	Returns
	--------------------
		Bool				--	True if new clip is better than old one. False otherwise
	"""
	new_len = new_e - new_s
	old_len = old_e - old_s
	return True if (new_len > old_len) else False

def get_good_timestamps( good_timestamps, data_file, offset):
	"""
	Adds correctly recognized words and their timestamps to good_timestamps

	Parameters
	--------------------
		good_timestamps		-- 	a dict of timestamps that are highly accurate.
							'word': (start_time, end_time) --> string: (double, double)
		datafile			-- 	JSON file of Watson's generated text, containing
							word guesses, start and end times, confidence levels, etc.
							This will most likely have some incorrect speech-to-text translations.
		offset				-- The amount by which we change the timestamp

	Returns
	--------------------
		nothing, but good_timestamps is modified.
	"""

	data = json.load(data_file)

	if 'results' in data:
		for res in data['results']:
			for word_alternatives in res['word_alternatives']:
				pred_word = word_alternatives['alternatives'][0]

				if pred_word['confidence'] > 0.95:
					start = word_alternatives['start_time']
					end = word_alternatives['end_time']
					word = pred_word['word']

					if word in good_timestamps:
						prev_word_start, prev_word_end = good_timestamps[word]
						if not is_new_clip_better(word, start, end, prev_word_start, prev_word_end):
							continue

					tup = (start + offset, end + offset)
					good_timestamps[word] = tup

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

def extract_words(orig_clip, good_timestamps, offset, ID):
	"""
	Extract word clips from the input audio clip.

	Parameters
	--------------------
		orig_clip			-- 	The input audio clip that we want to extract word clips from
		good_timestamps		-- 	The timestamps of the words
		offset				--  How many seconds have passed

	Returns
	--------------------
		nothing
	"""
	for word, val in good_timestamps.items():
		start = val[0] + offset
		end = val[1] + offset

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

def remove_extra_clips():
	path = "clips/" + person + "/"
	assure_path_exists(path)
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

######################################################################
# main
######################################################################

def main(argv) :
	t0 = time.time()

	print(sys.argv[0])
	print(sys.argv[1])
	print(sys.argv[2])

	if(len(sys.argv) != 3): #TODO: change this to allow input transcript
		print('Usage: speech2text.py person inputfile')
		sys.exit(2)

	num_threads = detectCPUs()
	print("Using " + str(num_threads) + " threads...")

	#modifying global variables
	global basename
	global person
	global clip_len

	#open input file and convert to flac (assume  test file in same directory for now)
	basename = os.path.splitext(os.path.basename(sys.argv[2]))[0]
	file_ext = os.path.splitext(sys.argv[2])[1][1:]

	print(basename)
	print(file_ext)

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

	remove_extra_clips() # threads may have created word duplicates because they have been embarassingly parallelized.
	tlast = time.time()

	print("Total elapsed time: " + str(tlast-t0))
	# os.remove("/workspace")
	# os.remove("/workspacets")

if __name__ == "__main__" :
	main(sys.argv[1:])
