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
    """
    Gets the raw training data for a file, returning a dictionary where keys
    are characters and values are lists of lines that the character says.
    """
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
    """
    Cleans words of punctuation and returns the stems of verbs. NOTE: Stemmer
    is not functioning correctly for us, so we don't actually use it here.
    """
    stems = set() 
    for word in words: 
        for character in string.punctuation:
            word = word.replace(character, '')
        stems.add(word)
    return stems

def organize_raw_training_data(raw_training_data, stemmer):
    """
    Takes in raw training data and returns all the words used, a tuple of
    each word each character says, and a list of all the characters.
    """
    documents = []
    all_words = set()
    classes = set()
    for key in raw_training_data.keys(): 
        classes.add(key)
        character_words = () #tuple 
        unique_words = []
        for sentence in raw_training_data[key]: 
            curr_sentence = [] 
            if "..." in sentence:
                sentence = sentence.replace("...", " ")
            sentence = sentence.split(" ")
            for word in sentence:   
                for character in string.punctuation:
                    if character != "'":
                        word = word.replace(character, "")
                curr_sentence.append(word)
                all_words.add(word) 
            unique_words.append(curr_sentence)
            character_words = (unique_words, key)
        documents.append(character_words)
    words = preprocess_words(all_words, stemmer)
    return words, classes, documents

def create_training_data(words, classes, documents, stemmer):
    """
    Creates training data for all sentences and output data denoting who
    is speaking. NOTE: We don't end up using stemmer here, as it is
    not functioning correctly.
    """
    output = []
    training_data = []
    for tuple in documents: 
        for sentence in tuple[0]:
            curr_sentence_output = [] 
            bag = []
            for name in classes: 
                if name == tuple[1]: 
                    curr_sentence_output.append(1)
                else: 
                    curr_sentence_output.append(0)
            for word in words: 
                if word in sentence: 
                    bag.append(1)
                else: 
                    bag.append(0)
            training_data.append(bag)
            output.append(curr_sentence_output)
    return training_data, output

def sigmoid(z):
    """ Computes basic sigmoid formula """
    return 1 / (1 + np.exp(-z))

def sigmoid_output_to_derivative(output):
    """Convert the sigmoid function's output to its derivative."""
    return output * (1-output)

"""* * * TRAINING * * *"""
def init_synapses(X, hidden_neurons, classes):
    """Initializes our synapses (using random values)."""
    # Ensures we have a "consistent" randomness for convenience.
    np.random.seed(1)

    # randomly initialize our weights with mean 0
    synapse_0 = 2*np.random.random((len(X[0]), hidden_neurons)) - 1
    synapse_1 = 2*np.random.random((hidden_neurons, len(classes))) - 1

    return synapse_0, synapse_1

def feedforward(X, synapse_0, synapse_1):
    """Feed forward through layers 0, 1, and 2."""
    layer_0 = X
    layer_1 = sigmoid(np.dot(layer_0, synapse_0))
    layer_2 = sigmoid(np.dot(layer_1, synapse_1))
    return layer_0, layer_1, layer_2

def get_synapses(epochs, X, y, alpha, synapse_0, synapse_1):
    """Update our weights for each epoch."""
    # Initializations.
    last_mean_error = 1

    prev_synapse_0_weight_update = np.zeros_like(synapse_0)
    synapse_0_direction_count = np.zeros_like(synapse_0)

    prev_synapse_1_weight_update = np.zeros_like(synapse_1)
    synapse_1_direction_count = np.zeros_like(synapse_1)

    # Make an iterator out of the number of epochs we requested.
    for j in iter(range(epochs+1)):
        layer_0, layer_1, layer_2 = feedforward(X, synapse_0, synapse_1)

        # How much did we miss the target value?
        layer_2_error = y - layer_2

        if (j% 10000) == 0 and j > 5000:
            # If this 10k iteration's error is greater than the last iteration,
            # break out.
            if np.mean(np.abs(layer_2_error)) < last_mean_error:
                print("delta after "+str(j)+" iterations:" +
                      str(np.mean(np.abs(layer_2_error))) )
                last_mean_error = np.mean(np.abs(layer_2_error))
            else:
                print("break:", np.mean(np.abs(layer_2_error)), ">",
                      last_mean_error )
                break

        # What direction is the target l2? How much is the change for layer_2?
        layer_2_delta = layer_2_error * sigmoid_output_to_derivative(layer_2)

        # How much did each l1 value contribute to the l2 error
        # (according to the weights)?
        # (Note: .T means transpose and can be accessed via numpy!)
        layer_1_error = layer_2_delta.dot(synapse_1.T)

        # What direction is the target l1? How much is the change for layer_1?
        layer_1_delta = layer_1_error * sigmoid_output_to_derivative(layer_1)

        # Manage updates.
        synapse_1_weight_update = (layer_1.T.dot(layer_2_delta))
        synapse_0_weight_update = (layer_0.T.dot(layer_1_delta))

        if j > 0:
            synapse_0_direction_count += np.abs(((synapse_0_weight_update >
                                                  0)+0) -
                                                ((prev_synapse_0_weight_update
                                                  > 0) + 0))
            synapse_1_direction_count += np.abs(((synapse_1_weight_update >
                                                  0)+0) -
                                                ((prev_synapse_1_weight_update
                                                  > 0) + 0))

        synapse_1 += alpha * synapse_1_weight_update
        synapse_0 += alpha * synapse_0_weight_update

        prev_synapse_0_weight_update = synapse_0_weight_update
        prev_synapse_1_weight_update = synapse_1_weight_update

    return synapse_0, synapse_1


def save_synapses(filename, words, classes, synapse_0, synapse_1):
    """Save our weights as a JSON file for later use."""
    now = datetime.datetime.now()

    synapse = {'synapse0': synapse_0.tolist(), 'synapse1': synapse_1.tolist(),
               'datetime': now.strftime("%Y-%m-%d %H:%M"),
               'words': words,
               'classes': classes
              }
    synapse_file = "synapses.json"

    with open(synapse_file, 'w') as outfile:
        json.dump(synapse, outfile, indent=4, sort_keys=True)
    print("Saved synapses to:", synapse_file)


def train(X, y, words, classes, hidden_neurons=10, alpha=1, epochs=50000):
    """Train using specified parameters."""
    print("Training with {0} neurons and alpha = {1}".format(hidden_neurons,
                                                             alpha))

    synapse_0, synapse_1 = init_synapses(X, hidden_neurons, classes)

    # For each epoch, update our weights
    synapse_0, synapse_1 = get_synapses(epochs, X, y, alpha, synapse_0,
                                        synapse_1)

    # Save our work
    save_synapses("synapses.json", words, classes, synapse_0, synapse_1)


def start_training(words, classes, training_data, output):
    """Initialize training process and keep track of processing time."""
    start_time = time.time()
    X = np.array(training_data)
    y = np.array(output)

    train(X, y, words, classes, hidden_neurons=20, alpha=0.1, epochs=100000)

    elapsed_time = time.time() - start_time
    print("Processing time:", elapsed_time, "seconds")


"""* * * CLASSIFICATION * * *"""

def bow(sentence, words):
    """Return bag of words for a sentence."""
    stemmer = LancasterStemmer()

    # Break each sentence into tokens and stem each token.
    sentence_words = [stemmer.stem(word.lower()) for word in nltk.word_tokenize(sentence)]

    # Create the bag of words.
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
    return (np.array(bag))

def get_output_layer(words, sentence):
    """Open our saved weights from training and use them to predict based on
    our bag of words for the new sentence to classify."""

    # Load calculated weights.
    synapse_file = 'synapses.json'
    with open(synapse_file) as data_file:
        synapse = json.load(data_file)
        synapse_0 = np.asarray(synapse['synapse0'])
        synapse_1 = np.asarray(synapse['synapse1'])

    # Retrieve our bag of words for the sentence.
    x = bow(sentence.lower(), words)
    # This is our input layer (which is simply our bag of words for the sentence).
    l0 = x
    # Perform matrix multiplication of input and hidden layer.
    l1 = sigmoid(np.dot(l0, synapse_0))
    # Create the output layer.
    l2 = sigmoid(np.dot(l1, synapse_1))
    return l2

def classify(words, classes, sentence):
    """Classifies a sentence by examining known words and classes and loading our calculated weights (synapse values)."""
    error_threshold = 0.2
    results = get_output_layer(words, sentence)
    results = [[i,r] for i,r in enumerate(results) if r>error_threshold ]
    results.sort(key=lambda x: x[1], reverse=True)
    return_results =[[classes[r[0]],r[1]] for r in results]
    print("\nSentence to classify: {0}\nClassification: {1}".format(sentence, return_results))
    return return_results

def main():
    """ Main function that controls the Neural Network process """
    raw_training_data = get_raw_training_data("dialogue_data.csv")
    stemmer = LancasterStemmer()
    words, classes, documents = organize_raw_training_data(raw_training_data,
                                                           stemmer)
    training_data, output = create_training_data(words, classes, documents,
                                                 stemmer)
    start_training(list(words), list(classes), training_data, output)

    # Classify new sentences.
    classify(list(words), list(classes), "will you look into the mirror?")
    classify(list(words), list(classes), "mithril, as light as a feather, "
                                         "and as hard as dragon scales.")
    classify(list(words), list(classes), "the thieves!")

if __name__ == "__main__":
    main()
