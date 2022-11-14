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


import os
import sys
import time
from record_audio import run_recorder
from audio_to_text import wav_to_text
from neural_network.train_neural_net import create_and_train_neural_network, comprehend_text
from utils.helper import eprint

name_alternatives = [
    "elaina",
    "elena",
    "alina",
    "elina",
    "ilena",
    "ilina",
    "jennifer"
]

def run_elaina():
    trained_model, words, labels = create_and_train_neural_network(force_train=False, force_encode=False)
    time.sleep(3)
    
    while True:
        recorded = run_recorder()
        if recorded == True:
            input_text = wav_to_text()
            
            if input_text == None:
                print("Cannot understand your input...")
                continue
            
            # If name elaina is found
            for idx, name in enumerate(name_alternatives):
                
                if input_text.lower().find(name) != -1:
                    output = comprehend_text(trained_model, input_text, words, labels)
                    print(output)
                    break
                
                if idx == len(name_alternatives) - 1:
                    print(input_text.lower())
                    eprint("Text does not contain Elaina, skipping...", dev=True)
                
                
if __name__ == "__main__":
    run_elaina()