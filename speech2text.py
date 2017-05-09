#! /usr/bin/python3
from pydub import AudioSegment
import json
# from watson_developer_cloud import SpeechToTextV1
import conf #contains username and password to access Watson API

# #Watson Speech To Text API login info
# stt = SpeechToTextV1(
# 	username = conf.username, 
# 	password = conf.password,
# 	x_watson_learning_opt_out=True
# )

# #open desired file and convert to flac (assume  test file in same directory for now)
# audio_init = AudioSegment.from_file("test.mp4", "mp4")
# audio_init.export("tmp.flac", format="flac")
# with open("tmp.flac", 'rb') as audio: #Use Watson Speech API
# 	stt.models()
# 	stt.get_model('en-US_BroadbandModel')
# 	stt_result = stt.recognize(
# 		audio, content_type='audio/flac', timestamps=True, word_confidence=True, continuous=True, profanity_filter=False
# 	)

# 	print(json.dumps(stt_result, indent=2))


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

def main() :
	with open('speech-snippets/auto-industry.json') as data_file:    
		good_timestamps = prune_wrong_recog( None, data_file )

	sound = AudioSegment.from_wav("samples/obama-auto-industry-new-records.wav")

	for k, v in good_timestamps.iteritems():
		start = 1000 * v[0]
		end = 1000 * v[1]
		clip = sound[start:end]
		clip.export("clips/" + k + ".wav", format="wav")

if __name__ == "__main__" :
	main()
