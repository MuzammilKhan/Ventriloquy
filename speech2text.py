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
#Watson Speech To Text API login info
stt = SpeechToTextV1(
	username = conf.username, 
	password = conf.password,
	x_watson_learning_opt_out=True
)

num_threads = 3

basename = ""
file_ext = ""
person = ""
input_video = ""
offset_amt = 0


######################################################################
# functions
######################################################################
class myThread (threading.Thread): #used this as guide: https://www.tutorialspoint.com/python3/python_multithreading.htm
	def __init__(self, threadID, audio):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.audio = audio

	def run(self):
		print ("Starting " + self.name)
		endtime=len(self.audio)
		increment_by= 60000
		for i in range(self.threadID, endtime, increment_by):
			if(i + 60000 > endtime):
				audio_chunk = self.audio[i:endtime]
			else:
				audio_chunk = self.audio[i:i+60000]
			audio_chunk.export("workspace/" + str(self.threadID) + "_" + str(i) + ".wav", format="wav")

			#Use Watson Speech API on audio chunk
			with open("workspace/" + str(self.threadID) + "_" + str(i) + ".wav", 'rb') as audio:
				stt.models()
				stt.get_model('en-US_BroadbandModel')
				stt_result = stt.recognize(
					audio, content_type='audio/wav', timestamps=True, word_confidence=True, continuous=True, profanity_filter=False,
					word_alternatives_threshold=0.0
				)#the parameters above can be altered to effect the output of the api

				#dump response to a json file if we want to check it later then open it
				with open('speech-snippets/' + basename + '_' + str(i) + '.json', 'w') as data_file:
					json.dump(stt_result, data_file, indent=1)
				with open('speech-snippets/' + basename + '_' + str(i) + '.json') as data_file:
					good_timestamps = prune_wrong_recog(None, data_file, self.threadID * offset_amt / 1000)

				#clip audio into word clips
				extract_words(sys.argv[2], good_timestamps, sys.argv[1].lower(), i/1000)
		print ("Exiting " + self.name)


def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
	""" makes a new video file playing video file ``filename`` between
		the times ``t1`` and ``t2``. 
		Note: This function is from the moviepy library but it was buggy so I fixed it here"""
	name,ext = os.path.splitext(filename)
	if not targetname:
		T1, T2 = [int(1000*t) for t in [t1, t2]]
		targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)
	
	cmd = [get_setting("FFMPEG_BINARY"), "-y",
	  "-i", filename,
	  "-ss", "%0.2f"%t1,
	  "-t", "%0.2f"%(t2-t1),
	  targetname]
	
	subprocess_call(cmd)

def prune_wrong_recog( script, data_file, offset ):
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
				print(tup)
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

def extract_words(orig_clip, good_timestamps, person, seconds):
	"""
	Extract word clips from the input audio clip.

	Parameters
	--------------------
		orig_clip			-- 	The input audio clip that we want to extract word clips from
		good_timestamps		-- 	The timestamps of the words
		person 				-- 	The person whose voice this is
		seconds				--  How many seconds have passed

	Returns
	--------------------
		nothing 
	"""
	special_chars = ['<', '>', '\\', '/', '*', ':', '?', '\"'] # used later to detect special characters

	for cur, nxt in zip(good_timestamps, good_timestamps[1:]+[(None, float("inf"), None)]):
		word = cur[0]
		start =  seconds + cur[1]
		cur_end =  seconds + cur[2]
		nxt_start =  seconds + nxt[1]

		end = cur_end #if (cur_end + 0.1 < nxt_start) else nxt_start
		
		no_special_char = True
		#check for special chars b/c windows doesn't allow these in filenames
		for char in special_chars:
			if char in word:
				no_special_char = False
				break

		if no_special_char:
			path = "clips/" + person + "/" + word.lower() + "/"
			assure_path_exists(path)
			num_clips = len(glob.glob(path + '*')) # get num of clips already in folder, to avoid overwiting
			ffmpeg_extract_subclip(orig_clip, start, end, targetname=(path  + str(num_clips + 1) + ".mp4"))


######################################################################
# main
######################################################################

def main(argv) :
	if(len(sys.argv) != 3): #TODO: change this to allow input transcript
		print('Usage: speech2text.py person inputfile')
		sys.exit(2)

	#open input file and convert to flac (assume  test file in same directory for now)
	basename = os.path.splitext(os.path.basename(sys.argv[2]))[0]
	file_ext = os.path.splitext(sys.argv[2])[1][1:]
	audio_init = AudioSegment.from_file(sys.argv[2], file_ext) #assuming input files are all supported by ffmpeg
	audio_chunk = AudioSegment.silent(duration=0) 
	endtime=len(audio_init)

	if os.path.exists("workspace"):
		shutil.rmtree("workspace") #clear workspace and remake it
		os.makedirs("workspace")
	else:
		os.makedirs("workspace")

	clip_len = endtime/ num_threads
	threads = []
	for i in range(0,num_threads): 
		if  i == num_threads -1:
			audio_chunk = audio_init[i * clip_len: endtime ]
		else:
			audio_chunk = audio_init[i * clip_len: (i+1) * clip_len]
		thread = myThread(i, audio_chunk)
		thread.start()
		threads.append(thread)

	for t in threads:
		t.join()




	# increment_by= 60000 * num_threads
	# for i in range(thread.threadID, endtime, increment_by):


	# for i in range(0,endtime, 60000): #chunk audio file into 60s segments
	# 	if(i + 60000 > endtime):
	# 		audio_chunk = audio_init[i:endtime]
	# 	else:
	# 		audio_chunk = audio_init[i:i+60000]
	# 	audio_chunk.export("workspace/" + str(i) + ".wav", format="wav")

	# 	#Use Watson Speech API on audio chunk
	# 	with open("workspace/" + str(i) + ".wav", 'rb') as audio:
	# 		stt.models()
	# 		stt.get_model('en-US_BroadbandModel')
	# 		stt_result = stt.recognize(
	# 			audio, content_type='audio/wav', timestamps=True, word_confidence=True, continuous=True, profanity_filter=False,
	# 			word_alternatives_threshold=0.0
	# 		)#the parameters above can be altered to effect the output of the api

	# 		#dump response to a json file if we want to check it later then open it
	# 		with open('speech-snippets/' + basename + '_' + str(i) + '.json', 'w') as data_file:
	# 			json.dump(stt_result, data_file, indent=1)
	# 		with open('speech-snippets/' + basename + '_' + str(i) + '.json') as data_file:
	# 			good_timestamps = prune_wrong_recog(None, data_file)  #TODO: add script to arguments of this file

	# 		#clip audio into word clips
	# 		extract_words(sys.argv[2], good_timestamps, sys.argv[1].lower(), i/1000)


if __name__ == "__main__" :
	main(sys.argv[1:])