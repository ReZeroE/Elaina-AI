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


import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import os
import sys
import numpy
import tflearn
import tensorflow
import random
import json
import pickle


CONFIDENCE_THRESHOLD = 0.8



DATA_FILE_NAME = "intents.json"
DATA_FILE_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE_NAME)

DL_MODEL_NAME = "elaina_model.tflearn"
DL_MODEL_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"training_models/{DL_MODEL_NAME}")

TRAINED_DATA = "elaina_data.pickle"
TRAINED_DATA_ABSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"trained_data/{TRAINED_DATA}")

with open(DATA_FILE_ABSPATH) as file:
    data = json.load(file)


def encode_training_data():
    # =====================================
    # ======| READING TRAINING DATA |======
    # =====================================

    words   = []     # all the words from patterns
    labels  = []     # basically tags
    docs    = []

    docs_x  = []     # List of all patterns tokenized into words
    docs_y  = []     # List of tags corresponding to the pattern in docs_x

    # Explanation:
    # docs_x = [pattern1, pattern2, pattern3]  
    # docs_y = [tag1    , tag1,     tag2]
    #    patter1 = ["how", "are", "you"]
    #    tag1    = "greetings"
    # Tags can have duplciates. They simply correspond to the pattern

    for intent in data['intents']:
        for pattern in intent['patterns']:
            
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])
            
        # Load all labels
        if intent['tag'] not in labels:
            labels.append(intent['tag'])

    # Stem words and remove duplicate words
    # Stem will remove prefix, suffix or infix for word 
    #   EX: stem([plays, playing, play]) -> [play, play, play]
    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)



    # ================================
    # ======| ONE-HOT ENCODING |======
    # ================================

    training    = []    # List of bags
    output      = []    # List of outputs

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []    # One-Hot Encoded Bag (order matters)
        wrds = [stemmer.stem(w) for w in doc]

        # Generate one-hot on the patterns
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
                
        # Generate one-hot based on the tags
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        
        training.append(bag)
        output.append(output_row)
        
        try:
            with open(TRAINED_DATA_ABSPATH, "wb") as wf:
                pickle.dump(words, labels, training, output, wf)
        except:
            pass
        
    return training, output, words, labels
    


def create_neural_network(training_data, output_data, force_train):
    """
    Create neural network model for training. Based on One-hot Encoded data.
    :param training_data: Out-hot encoded input data
    :param output_data: One-hot encoded output data
    """
    
    # ================================
    # ======| NEURAL NETWORK |========
    # ================================

    # Reformat into numpy arrays for training
    training    = numpy.array(training_data)    # np.array of bags
    output      = numpy.array(output_data)      # np.array of outputs

    tensorflow.compat.v1.reset_default_graph()

    # Input Layer
    training_row_length = len(training[0])
    net = tflearn.input_data(shape=[None, training_row_length])

    # Hidden Layer (fully connected with 8 neurons)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    

    # Output Layer (softwax activation [output highest neuron probability])
    output_row_length = len(output[0])
    net = tflearn.fully_connected(net, output_row_length, activation="softmax")    

    # Create neural network model
    net = tflearn.regression(net)
    model = tflearn.DNN(net)

    # Fit data 
    n_epoch     = 5000      # number of times to feed the model the same data
    batch_size  = 16         # number of batch per training run
    show_metric = True      # basically verbose training
    
    if force_train == False:
        try:    # Try to load model if exists
            model.load(DL_MODEL_ABSPATH)
        except: # If model does not exist, train model (fit data)
            model.fit(training, output, n_epoch=n_epoch, batch_size=batch_size, show_metric=show_metric)
            model.save(DL_MODEL_ABSPATH)
    
    else: # Force train the model
        model.fit(training, output, n_epoch=n_epoch, batch_size=batch_size, show_metric=show_metric)
        model.save(DL_MODEL_ABSPATH)

    return model


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    
    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    
    return numpy.array(bag)            


def setup_neural_net(force_encode=False, force_train=False):
    """
    Elaina neural network driver.
    1. Encode Training Data
    2. Create Neural Network
    
    :param force_train: Train new model regardless whether it already exist or not
    :return: The NL trained model
    """
    
    # =====| DATA ENCODE |=====
    if force_encode == True:  # Force to reencode all data
        training_data = encode_training_data()
        input_training_data  = training_data[0]
        output_training_data = training_data[1]
        words                = training_data[2]  # all the words from patterns
        labels               = training_data[3]
    
    else: # Not forced to reencode all data
        try:    # Load encoded data if already exists
            with open(TRAINED_DATA_ABSPATH, "rb") as rf:
                words, labels, training, output = pickle.load(rf)
                
            input_training_data  = training
            output_training_data = output
        except: # Encode data if those data does not exist yet 
            training_data = encode_training_data()
            input_training_data  = training_data[0]
            output_training_data = training_data[1]
            words                = training_data[2]  # all the words from patterns
            labels               = training_data[3]
    
    # =====| MODEL TRAINING |=====
    trained_model = create_neural_network(input_training_data, output_training_data, force_train)
    return trained_model, words, labels


def comprehend_text(trained_model, input_text, words, labels):
    """
    Comprehend user texts and outputs the corresponding tag. Returns None if input cannot be understood.
    :param input_text: User input text to understand
    :words: patters words list
    :labels: all labels
    """
    # Predict output
    results = trained_model.predict([bag_of_words(input_text, words)])
    print(results)
    
    # Select output with the highest probability
    result_index = numpy.argmax(results)
    tag = labels[result_index]
    
    # Check prediction confidence
    if results[0][result_index] > CONFIDENCE_THRESHOLD:
        return tag
    else:
        return None

if __name__ == "__main__":
    trained_model, words, labels = setup_neural_net(force_encode=True, force_train=True)
    output = comprehend_text(trained_model, " is it raining outside", words, labels)
    
    print(f"Predicted: {output}")