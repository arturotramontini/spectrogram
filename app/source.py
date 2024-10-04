import config
import librosa 

import matplotlib.pyplot as plt
import librosa.display


import math
import numpy as np
import pyaudio
import time

from utils import logger




class Source:

	def __init__(self, *args, **kwargs):
	
		self.t1 = time.time()		
		
		self.audio = pyaudio.PyAudio()
		self.complete = False
		self.data = []
		self.index = 0
		self.total = 0
		self.hop_size = config.HOP_SIZE
		self.hop_cnt = 20
		self.init(*args, **kwargs)

	def init(*args, **kwargs):
		raise NotImplementedError('source.init')
	
	def callback(self, data, frame_count, time_info, status):
		raise NotImplementedError('source.callback')

	def get(self):
		if self.index + config.WINDOW_SIZE > self.total:
			return None
		a = self.index
		b = self.index + config.WINDOW_SIZE
		data = self.data[a:b]
		self.index = a + self.hop_size  # config.HOP_SIZE
		return np.array(data)

	def available(self):
		samples = self.total - self.index
		samples -= config.WINDOW_SIZE
		available = math.ceil(samples / self.hop_size )  # config.HOP_SIZE)

		self.hop_cnt -= 1
		if self.hop_cnt < 1:
			self.hop_cnt = 10
			if available < 30:
				self.hop_size -= 1
			if available > 40:
				self.hop_size += 1

		return max(0, available)

	def release(self):
		self.stream.close()
		self.audio.terminate()







class File(Source):
	
	def init(self, filename):
		self.data, _ = librosa.load(filename, sr=config.SAMPLE_RATE)
		self.stream = self.audio.open(
				format=pyaudio.paFloat32,
				channels=1,
				rate=config.SAMPLE_RATE,
				output=True,
				frames_per_buffer=config.BUFFER_SIZE,
				stream_callback=self.callback)

	def callback(self, in_data, frame_count, time_info, status):
		a = self.total
		b = self.total + config.BUFFER_SIZE
		data = self.data[a:b]
		self.total = b
		if self.total >= len(self.data):
			self.complete = True
		return (data, pyaudio.paContinue)
	
	# def get(self):
		# if self.index + config.WINDOW_SIZE > self.total:
		# 	return None
		# a = self.index
		# b = self.index + config.WINDOW_SIZE
		# data = self.data[a:b]
		# self.index = a + config.HOP_SIZE
		# return np.array(data)

	# def available(self):
	# 	samples = self.total - self.index
	# 	samples -= config.WINDOW_SIZE
	# 	available = math.ceil(samples / config.HOP_SIZE)
	# 	return max(0, available)

	# def release(self):
	# 	self.stream.close()
	# 	self.audio.terminate()
		

class Microphone(Source):

	def init(self):
		# Create audio stream
		self.stream = self.audio.open(
			format=pyaudio.paFloat32,
			channels=1,
			rate=22050,  # config.SAMPLE_RATE,
			input=True,
			frames_per_buffer= 8182, # 1024,  # config.BUFFER_SIZE,
			stream_callback=self.callback)

	def callback(self, data, frame_count, time_info, status):
		t2 = time.time()
		dt = t2 -self.t1
		self.t1 = t2
		# print(f'dt: {dt:0.3f}')
		data = np.frombuffer(data, dtype=np.float32)
		data = data.tolist()
		self.data.extend(data)
		self.total = len(self.data)
		return None, pyaudio.paContinue
	

if __name__ == '__main__':
	filename = './audio/gettysburg.wav'
	source = File(filename)
	time.sleep(20)
