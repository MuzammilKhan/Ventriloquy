#! /usr/bin/python3
import sys
import os
import glob
import shutil
from pydub import AudioSegment
import json
from watson_developer_cloud import SpeechToTextV1
import conf #contains username and password to access Watson API
import imageio
imageio.plugins.ffmpeg.download()
from moviepy.tools import subprocess_call
from moviepy.config import get_setting

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

def prune_wrong_recog( script, data_file ):
	"""
	Returns the correctly recognized words and their timestamps.

	Parameters
    --------------------
        script			-- 	Array of transcript of a speech. This is assumed to be completely correct.
        datafile		-- 	JSON file of Watson's generated text, containing 
        				word guesses, start and end times, confidence levels, etc.
        				This will most likely have some incorrect speech-to-text translations.

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
				start_time = word_alternatives['start_time']
				end_time = word_alternatives['end_time']
				pred_word = word['word']
				tup = (pred_word, start_time, end_time) 
				good_timestamps.append(tup)

	return good_timestamps

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
    	os.makedirs(dir)

######################################################################
# main
######################################################################

def main(argv) :
	if(len(sys.argv) != 2): #TODO: change this to allow input transcript
		print('Usage: speech2text.py inputfile')
		sys.exit(2)

	#Watson Speech To Text API login info
	stt = SpeechToTextV1(
		username = conf.username, 
		password = conf.password,
		x_watson_learning_opt_out=True
	)

	#open input file and convert to flac (assume  test file in same directory for now)
	basename = os.path.splitext(os.path.basename(sys.argv[1]))[0]
	file_ext = os.path.splitext(sys.argv[1])[1][1:]
	audio_init = AudioSegment.from_file(sys.argv[1], file_ext) #assuming input files are all supported by ffmpeg
 	
	if os.path.exists("workspace"):
		shutil.rmtree("workspace") #clear workspace and remake it
		os.makedirs("workspace")
	else:
	    os.makedirs("workspace")

   	special_chars = ['<', '>', '\\', '/', '*', ':', '?', '\"'] # used later to detect special characters
	audio_chunk = AudioSegment.silent(duration=0) 
	endtime=len(audio_init)
	for i in range(0,endtime, 60000): #chunk audio file into 60s segments
		if(i + 60000 > endtime):
			audio_chunk = audio_init[i:endtime]
		else:
			audio_chunk = audio_init[i:i+60000]
		audio_chunk.export("workspace/" + str(i) + ".wav", format="wav")

	 	#Use Watson Speech API on audio chunk
		with open("workspace/" + str(i) + ".wav", 'rb') as audio:
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
				good_timestamps = prune_wrong_recog(None, data_file)  #TODO: add script to arguments of this file

			#clip audio into word clips
			for cur, nxt in zip(good_timestamps, good_timestamps[1:]+[(None, float("inf"), None)]):
				word = cur[0]
				start = 1000 * cur[1]
				cur_end = 1000 * cur[2]
				nxt_start = 1000 * nxt[1]

				end = cur_end if (cur_end + 100 < nxt_start) else nxt_start

				clip = audio_chunk[start:end]

				no_special_char = True
				#check for special chars b/c windows doesn't allow these in filenames
				for char in special_chars:
					if char in word:
						no_special_char = False
						break

				if no_special_char:
					path = "clips/" + word + "/"
					assure_path_exists(path)
					num_clips = len(glob.glob(path + '*')) # get num of clips already in folder, to avoid overwiting
					clip.export(path + str(num_clips + 1) + ".wav", format="wav")


if __name__ == "__main__" :
	main(sys.argv[1:])
