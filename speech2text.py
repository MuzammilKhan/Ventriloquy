#! /usr/bin/python3
import sys
import os
from pydub import AudioSegment
import json
from watson_developer_cloud import SpeechToTextV1
import conf #contains username and password to access Watson API


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

	good_timestamps = {}

	data = json.load(data_file)
	for word_alternatives in data['results'][0]['word_alternatives']:
		word = word_alternatives['alternatives'][0]
		if word['confidence'] > 0.95:
			start_time = word_alternatives['start_time']
			end_time = word_alternatives['end_time']
			good_timestamps[word['word']] = (start_time, end_time)

	return good_timestamps

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
	print(basename)
	print(file_ext)
	audio_init = AudioSegment.from_file(sys.argv[1], file_ext) #assuming input files are all supported by ffmpeg
	audio_init.export("tmp.wav", format="wav")
 	
 	#Use Watson Speech API on input file
	with open("tmp.wav", 'rb') as audio:
		stt.models()
		stt.get_model('en-US_BroadbandModel')
		stt_result = stt.recognize(
			audio, content_type='audio/wav', timestamps=True, word_confidence=True, continuous=True, profanity_filter=False,
			word_alternatives_threshold=0.0
		)#the parameters above can be altered to effect the output of the api

		#dump response to a json file if we want to check it later then open it
		with open('speech-snippets/' + basename + '.json', 'w') as data_file:
			json.dump(stt_result, data_file, indent=1)
		with open('speech-snippets/' + basename + '.json') as data_file:
			good_timestamps = prune_wrong_recog(None, data_file)  #TODO: add script to arguments of this file

		#clip audio into word clips
		for k, v in good_timestamps.items():
			start = 1000 * v[0]
			end = 1000 * v[1]
			clip = audio_init[start:end]
			clip.export("clips/" + k + ".wav", format="wav")


if __name__ == "__main__" :
	main(sys.argv[1:])
