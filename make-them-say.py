#! /usr/bin/python3
import sys
import os
from pydub import AudioSegment

# def find(name, path):
#     for root, dirs, files in os.walk(path):
#         if name in files:
#             return os.path.join(root, name)

def main(argv) :
	if(len(sys.argv) != 2): 
		print('Usage: make-them-say.py statement')
		sys.exit(2)

	phrase = os.path.splitext(sys.argv[1])[0]
	words = phrase.split()

	combined_audio = AudioSegment.silent(duration=0) 
	
	for word in words:
		audio = AudioSegment.from_wav("clips/" + word + ".wav")
		combined_audio += audio #+ AudioSegment.silent(duration=0.75) 

	combined_audio.export("output/they-say.wav", format="wav")

if __name__ == "__main__" :
	main(sys.argv[1:])