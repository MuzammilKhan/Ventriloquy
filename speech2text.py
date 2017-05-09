#! /usr/bin/python3
from pydub import AudioSegment
import json
from watson_developer_cloud import SpeechToTextV1
import conf #contains username and password to access Watson API

#Watson Speech To Text API login info
stt = SpeechToTextV1(
	username = conf.username, 
	password = conf.password,
	x_watson_learning_opt_out=True
)

#open desired file and convert to flac (assume  test file in same directory for now)
audio_init = AudioSegment.from_file("test.mp4", "mp4")
audio_init.export("tmp.flac", format="flac")
with open("tmp.flac", 'rb') as audio: #Use Watson Speech API
	stt.models()
	stt.get_model('en-US_BroadbandModel')
	stt_result = stt.recognize(
		audio, content_type='audio/flac', timestamps=True, word_confidence=True, continuous=True, profanity_filter=False
	)

	print(json.dumps(stt_result, indent=2))


def prune-wrong-recog( script, text ):
	"""Returns the correctly recognized words and their timestamps.
	
	Parameters
    --------------------
        script   -- Transcript of a speech. This is assumed to be completely correct.
        text     -- Watson's generated text. This will most likely have some incorrect speech-to-text translations.

    Returns
    --------------------
        pruned-text -- dict of words to timestamps. These will be completely accurate

	"""

