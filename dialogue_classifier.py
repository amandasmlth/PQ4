import nltk
from nltk.stem.lancaster import LancasterStemmer
import os
import json
import datetime
import csv
import numpy as np
import time
import string

def get_raw_training_data(filename): 
    training_data = {}
    with open(filename, 'r') as infile:
        reader = csv.reader(infile)
        for line in reader: 
            if line[0] in training_data.keys():
                training_data[line[0]].append(line[1].lower())
            else: 
                training_data[line[0].lower()] = [line[1].lower()]
    return training_data

def preprocess_words(words, stemmer): 
    words = words.split(" ")
    stems = set() 
    for word in words: 
        for character in string.punctuation:
                word = word.replace(character, '')
        stems.add(stemmer.stem(word)) #note: come back here when done because the stemmer should only create stems for verbs not other parts of speech 
    return stems

def main(): 
    training_data = get_raw_training_data("dialogue_data.csv")
    stemmer = LancasterStemmer()
    print(preprocess_words(training_data['galadriel'][0], stemmer))
    #print(stemmer.stem("swimming"))

if __name__ == "__main__":
    main()