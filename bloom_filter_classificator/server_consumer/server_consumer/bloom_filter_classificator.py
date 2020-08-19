import time
import os
import re
import numpy as np
import string
import collections
from pympler import asizeof
from bloom_filter import BloomFilter
from nltk.stem import WordNetLemmatizer 
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords 
from stop_words import get_stop_words
import logging


logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s')


class BloomClassificator():

    def __init__(self, dict_of_classes_with_training_files, max_elements=2000000, error_rate=0.00001):
        self.blooms = {}
        self.classification_result = []
        self.stop_words = set(stopwords.words("english") + get_stop_words('english'))

        for model in dict_of_classes_with_training_files:
            self.blooms[model] = BloomFilter(max_elements=max_elements, error_rate=error_rate)

            print('Size of initializing Bloom Filter: {} Kb'.format(asizeof.flatsize(self.blooms[model])/1000))
            # print('num_bits_m = {}'.format(self.blooms[model].num_bits_m))
            # print('num_probes_k = {}'.format(self.blooms[model].num_probes_k))
            # print('len array of Int32 = {}'.format(len(self.blooms[model].backend.array_)))
            # print('size of array of Int32 = {} Kb'.format(asizeof.flatsize(self.blooms[model].backend.array_)/1000))
            # print('\n')

            # TRAINING MODEL
            # print('Start training model "{}"'.format(model))
            start_overall = time.time()
            for file_path in dict_of_classes_with_training_files[model]:
                with open(file_path, errors='ignore') as f:
                    start = time.time()
                    for word in self.text_preprocessing(" ".join(f.readlines()), os.path.basename(file_path)):
                        self.blooms[model].add(word)
                    # print('Time training text {}: {}'.format(file_path, time.time() - start))
            print('\nTime for training model {}: {}'.format(model, time.time() - start_overall))
            print('________________________________________________________________\n')

    def text_preprocessing(self, text, file_name):
        start = time.time()
        # Text Lowercase
        text = text.lower()
        # Remove numbers and punctuation
        text = re.sub(r'[\W\d]+', ' ', text)
        # Remove stopwords
        text = " ".join([word for word in text.split() if word not in self.stop_words])
        # Lemmatization
        lemmatizer = WordNetLemmatizer()
        lemmas = [lemmatizer.lemmatize(word) for word in word_tokenize(text)]

        # print('Time preprocessing text {}: {}'.format(file_name, time.time() - start))
        # print('Len of lemmas in text {}: {}'.format(file_name, len(lemmas)))
        return lemmas

    def classification(self, text, file=False, additional_training=True, weight_of_text_to_train=0.7, weight_of_word_to_train=0.005):
        # print('START CLASSIFICATION {}'.format(text if file == True else ''))

        if not (0 <= weight_of_text_to_train <= 1):
            print('ERROR: weight_of_text_to_train have to be between 0 and 1')
            return
        if not (0 <= weight_of_word_to_train <= 1):
            print('ERROR: weight_of_word_to_train have to be between 0 and 1')
            return
        if file == True and not os.path.exists(text):
            print('ERROR: if file=True, "text" should be path to file')
            return

        start = time.time()
        if file == True:
            file = text
            with open(file, errors='ignore') as f:
                text = " ".join(f.readlines())

        words = self.text_preprocessing(text, file)

        p = {}
        for model in self.blooms:
            p[model] = self._get_probability(words, self.blooms[model])
            # print('Probability {} = {}'.format(model, p[model]))

        if set(p.values()) == 1:
            print('Text equally belongs to each class')
            # print('Time for classification: {}\n'.format(time.time() - start))
            self.classification_result.append((file if file else None, None, round(list(p.values())[0], 3), round(time.time() - start, 3)))
        else:
            model_of_text = max(p, key=lambda key: p[key])
            print('Text belongs to {}'.format(model_of_text.upper()))
            # print('Time for classification: {}\n'.format(time.time() - start))
            self.classification_result.append((file if file else None, model_of_text, round(p[model_of_text], 3), round(time.time() - start, 3)))

            if additional_training:
                # print('Additional training for class "{}"'.format(model_of_text))
                max_p = max(p.values())
                if max_p >= weight_of_text_to_train:
                    self.blooms[model_of_text] = self._additional_training(words, self.blooms[model_of_text], weight_of_word_to_train)
                else:
                    print('Additional training is not perform as P < {}, P = {}'.format(weight_of_text_to_train, max_p))

        # print('________________________________________________________________\n')

    def _get_probability(self, words, bloom):
        start = time.time()
        num_words_in_bloom = 0
        for word in words:
            if word in bloom:
                num_words_in_bloom += 1
        p = num_words_in_bloom / len(words)
        # print('Time getting probability: {}'.format(time.time() - start))
        return p

    def _additional_training(self, word_lemmas, bloom, weight_of_word_to_train=0):
        if not (0 <= weight_of_word_to_train <= 1):
            print('ERROR: weight_of_word_to_train have to be between 0 and 1')
            return bloom

        start = time.time()
        bag_of_words = collections.Counter(word_lemmas)
        len_words = len(word_lemmas)
        words_to_train = [word for word in bag_of_words if bag_of_words['word'] / len_words >= weight_of_word_to_train]
        for word in words_to_train:
            bloom.add(word)
        # print('Words for additional training:\n{}'.format(words_to_train))
        # print('Time for additional training: {}'.format(time.time() - start))
        return bloom


if __name__ == '__main__':
    dict_of_classes_with_training_files = {}
    dict_of_classes_with_training_files['Football'] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_football', text) for text in os.listdir('training_football')]
    dict_of_classes_with_training_files['Basketball'] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_basketball', text) for text in os.listdir('training_basketball')]
    dict_of_classes_with_training_files['Traveling'] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_travel', text) for text in os.listdir('training_travel')]

    bloom_classificator = BloomClassificator(dict_of_classes_with_training_files)
    for file in os.listdir('texts_to_classify'):
        bloom_classificator.classification(os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts_to_classify", file), True, False)
    without_training = bloom_classificator.classification_result
    bloom_classificator.classification_result = []

    for file in os.listdir('texts_to_classify'):
        bloom_classificator.classification(os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts_to_classify", file), True)
    with_training = bloom_classificator.classification_result

    print('\nTime classification result without training: {}'.format(sum([i[3] for i in without_training])))
    print('Classification result without training:\n')
    print('Path to text for classification   \t| Class   \t| P % \t| Time\t| Result')
    print('____________________________________________________________________________________')
    for tup in without_training:
        print('\t| '.join([str(i) for i in tup] + [str(tup[1].lower() in tup[0].lower())]))
    
    print('\nTime classification result with training: {}'.format(sum([i[3] for i in with_training])))
    print('Classification result with training:\n')
    print('Path to text for classification   \t| Class   \t| P % \t| Time\t| Result')
    print('____________________________________________________________________________________')
    for tup in with_training:
        print('\t| '.join([str(i) for i in tup] + [str(tup[1].lower() in tup[0].lower())]))
