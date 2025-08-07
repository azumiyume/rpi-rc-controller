import os
import subprocess

class AudioPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.process = None

    def play(self):
        self.process = subprocess.Popen(["mpg123", self.filename])

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
