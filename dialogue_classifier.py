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

def organize_raw_training_data(raw_training_data, stemmer):
    all_characters = []
    for key in raw_training_data.keys(): 
        character_words = ()
        unique_words = set()
        for sentence in raw_training_data[key]: 
            sentence = sentence.split(" ")
            for word in sentence: 
                unique_words.add(word)
        character_words = (unique_words, key)
        all_characters.append(character_words)
    return all_characters

def main(): 
    training_data = get_raw_training_data("dialogue_data.csv")
    stemmer = LancasterStemmer()
    #reprocess_words(training_data['galadriel'][0], stemmer)
    print(organize_raw_training_data(get_raw_training_data("dialogue_data.csv"), stemmer))
    #print(stemmer.stem("swimming"))

if __name__ == "__main__":
    main()