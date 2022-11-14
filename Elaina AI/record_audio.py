#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2022 Kevin Liu
# Elaina Voice Assistant (single & multi core) 
# MIT License
# Hosted at: https://github.com/ReZeroE/Elaina-Voice-Assistant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import pyaudio
import math
import struct
import wave
import time
import os
from utils.helper import eprint

# =============================
# ======| Audio Presets |======
# =============================

SHORT_NORMALIZE = (1.0/32768.0)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
TIMEOUT_LENGTH = 1


# =============================
# ====| Recording Presets |====
# =============================

recording_file_name     = "user_audio.wav"
recording_dir_name      = "audio_recordings"
recording_dir_abspath   = os.path.join(os.path.dirname(os.path.abspath(__file__)), recording_dir_name)


# ==============================
# ======| Recorder Class |======
# ==============================

class Recorder:
    @staticmethod
    def rms(frame):
        """
        Function for measuring the rms (loudness) of the frame.
        :param frame: recorded frame
        """
        swidth = 2
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000


    def __init__(self):
        """
        Recorder initialization function.
        """
        self.rms_threshold      = 10    # The threshold for rms (to start recording)
        self.audio_buffer       = []    # Head audio buffer frames list
        self.audio_buffer_len   = 10    # Head buffer frames count (increase to add a longer buffer)
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=CHUNK)
        

    def record(self):
        """
        Record audio by a given number of frames.
        """
        print('[Elaina] Sound detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:
            data = self.stream.read(CHUNK)
            if self.rms(data) >= self.rms_threshold: 
                end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(self.audio_buffer + rec))


    def buffer_audio_frames(self, audio_input):
        """
        Creates buffer
        """
        if self.audio_buffer_len == 0:
            return
        
        if len(self.audio_buffer) == self.audio_buffer_len:
            self.audio_buffer.pop(0)
            
        self.audio_buffer.append(audio_input)


    def listen(self, once=False):
        """
        Listens on audio for recording (if rms > threshold).
        :param once: only listen to and record one audio input (don't loop)
        """
        eprint("Listening", user=True)
        while True:
            input = self.stream.read(CHUNK)
            self.buffer_audio_frames(input)
            rms_val = self.rms(input)
            if rms_val > self.rms_threshold:
                self.record()
                
                # Only listen for 1 audio input, then breaks
                if once == True:
                    return True

    
    def calibrate_background_noise(self):
        """
        Function for calibrating the background noise to set the rms threshold.
        """
        eprint("Calibrating background noises...", user=True)
        s = time.time()
        rmss = []
        while True:
            if time.time() - s > 1:
                break
            input = self.stream.read(CHUNK)
            rmss.append(self.rms(input))
            self.rms_threshold = sum(rmss) / len(rmss)
            
        self.rms_threshold += 15
        

    def write(self, recording):
        """
        Helper function for writing the audio file recorded (.wav)
        :param recording: list of audio frames
        """
        filename = os.path.join(recording_dir_abspath, recording_file_name)

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        
        eprint(f'Written to file: {filename}', dev=True)


def run_recorder():
    a = Recorder()
    a.calibrate_background_noise()
    print(a.rms_threshold)
    ret = a.listen(once=True)
    
    return ret
    
if __name__ == "__main__":
    run_recorder()
