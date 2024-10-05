import config
from rect import Rect
from source import File, Microphone
from spec import Spec
from text import Text
from ticks import Ticks
from wave1 import Wave
from window import Window
from utils import logger


class App(Window):
	def init(self):
		logger.info(f"init")
		# self.source = File('audio/gettysburg.wav')
		self.source = Microphone()
		self.nodes = []
		self.wave = Wave(self.ctx, 0, 0, config.WINDOW_WIDTH, 200)
		self.nodes.append(self.wave)
		self.spec = Spec(self.ctx, 0, self.wave.h, config.WINDOW_WIDTH, 460)
		self.nodes.append(self.spec)
		bg_color = (0.06, 0.06, 0.07, 1)
		bg_color2 = (0.06, 0.06, 0.17, 1)
		# Wave separation line
		self.nodes.append(
			Rect(self.ctx, 0, self.wave.h, config.WINDOW_WIDTH, 2, bg_color)
		)
		# Time axis background
		# self.r1 = Rect(self.ctx, 0, 660, config.WINDOW_WIDTH, 70, bg_color)
		self.nodes.append(Rect(self.ctx, 0, 660, config.WINDOW_WIDTH, 70, bg_color))
		# Y_db axis background
		# self.r2 = Rect(self.ctx, 0, 0, 80, config.WINDOW_HEIGHT -72 , bg_color2)
		self.nodes.append(
			Rect(self.ctx, 0, 0, 80, config.WINDOW_HEIGHT - 72, bg_color2)
		)
		# Ticks
		# 1/20th second ticks
		self.nodes.append(
			Ticks(self.ctx, x=81, y=660, w=1200, h=15, gap=6, color=(0.3, 0.3, 0.4, 1))
		)
		# 1 second ticks
		self.nodes.append(
			Ticks(
				self.ctx, x=81, y=660, w=1200, h=25, gap=120, color=(0.4, 0.4, 0.5, 1)
			)
		)
		# 2000 Hz ticks
		pixels_per_freq = self.spec.h / 11046
		self.nodes.append(
			Ticks(
				self.ctx,
				x=70,
				y=self.spec.y + pixels_per_freq * 1046,
				w=10,
				h=pixels_per_freq * 10000,
				color=(0.4, 0.4, 0.5, 1),
				gap=pixels_per_freq * 2000,
				horizontal=False,
			)
		)
		# Text
		# Create text renderer
		text = Text(self.ctx)
		self.nodes.append(text)
		# Seconds text
		for i in range(1, 11):
			x = config.WINDOW_WIDTH - i * 120
			text.add(f"{i}s", x, 705, align="center")
		# Hz text
		for i in range(6):
			hz = i * 2000
			y = 660 - pixels_per_freq * hz + 4
			text.add(f"{hz}hz", 62, y, align="right")

	def size(self, w, h):
		# self.wave.size(w, h)
		# self.spec.size(w, h)
		# self.r1.size(w,h)
		# self.r2.size(w,h)
		for node in self.nodes:
			node.size(w, h)

	def draw(self, dt):
		available = self.source.available()
		# window = self.source.get()
		logger.info(f"{self.source.hop_cnt}, {self.source.hop_size}, {available}")
		# logger.info(f'{self.source.hop_cnt}, {self.source.hop_size}, {available}, {window.shape if window is not None else None}')
		# logger.info(f'{available}, {window.shape if window is not None else None}')
		# self.wave.add(window)
		for i in range(2):
			window = self.source.get()
			self.wave.add(window)
			self.spec.add(window)
		self.wave.update()
		self.spec.update()
		# self.wave.draw()
		# self.spec.draw()
		# self.r1.draw()
		# self.r2.draw()
		for node in self.nodes:
			node.draw()

	def exit(self):
		logger.info("exit")
		self.source.release()


if __name__ == "__main__":
	App.run()
