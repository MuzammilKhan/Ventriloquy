#! /usr/bin/python3
import sys
import os
from pydub import AudioSegment

# def find(name, path):
#     for root, dirs, files in os.walk(path):
#         if name in files:
#             return os.path.join(root, name)

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def main(argv) :
	if(len(sys.argv) != 2): 
		print('Usage: make-them-say.py statement')
		sys.exit(2)

	phrase = os.path.splitext(sys.argv[1])[0]
	words = phrase.split()
	combined_audio = AudioSegment.silent(duration=0)
	
	for word in words:
		if word == '-': #dashes seperated by space will insert extra silences
			audio = AudioSegment.silent(duration=100)
		else:
			audio = AudioSegment.from_wav("clips/" + word + "/1.wav")

		normalized_audio = match_target_amplitude(audio, -15.0)
		combined_audio += normalized_audio

		# crossed_audio = audio#.fade_in(len(audio)/150)#.fade_out(len(audio)/5)
		print(word + " - " + str(len(audio)))
		# combined_audio += audio

		# combined_audio += crossed_audio # + AudioSegment.silent(duration=35) 
		# combined_audio.append(audio, crossfade=(len(audio)/2))
		# combined_audio += AudioSegment.silent(duration=35) 

	combined_audio.export("output/they-say.wav", format="wav")

if __name__ == "__main__" :
	main(sys.argv[1:])