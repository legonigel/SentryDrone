import sys
from subprocess import call
import threading
import signal

class Video(threading.Thread):
	"""Video class to launch media flux"""
	def __init__(self, nom = ''):
		threading.Thread.__init__(self)
		self.process = None
	def run(self):
		print "Video"
		call(["ffplay", "tcp://192.168.1.1:5555/"])
	def stop(self):
		call(["killall", "ffplay"])
		if self.process is not None:
			self.process.terminate()
			self.process = None


if __name__ == '__main__':
    try:
	video = Video('Thread Video')
	video.start()
    except (KeyboardInterrupt, SystemExit):
	video.stop()
	sys.exit()
