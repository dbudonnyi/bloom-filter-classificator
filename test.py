
import time
import numpy as np
import pymongo
from pympler import asizeof 
from datasketch import HyperLogLogPlusPlus
from gibberish import Gibberish

def words_generator(n):
    start = time.time()
    gib = Gibberish()
    words = gib.generate_words(n)
    end = time.time()
    print('Time generating:: {}'.format(end - start))
    print('Real Number of words: {}'.format(len(words)))
    len_unique = len(set(words))
    print('Number of unique words: {}'.format(len_unique))
    print('Size of words: {} Mb, {} Kb'.format(asizeof.flatsize(words)/1024/1024, asizeof.flatsize(words)/1024))
    print('________________________________________________________________\n')
    return words, len_unique

def python_set(db, words):
    print('Standart python functionality (set())')
    collection = db.python_set
    collection.delete_many({})
    # unique_words = set()

    start = time.time()
    for word in words:
        unique_words = set([elem['word'] for elem in collection.find()])
        len_unique_words = len(unique_words)
        unique_words.add(word)
        if len(unique_words) > len_unique_words:
            collection.insert_one({'word': word})
        # unique_words.add(word)
    end = time.time()

    print('[python set()] Time python:: {}'.format(end - start))
    print('[python set()] Number of unique words: {}'.format(collection.count_documents({})))
    print('[python set()] Size of unique words: {} Mb, {} Kb\n'.format(asizeof.asizeof(unique_words)/1024/1024, asizeof.asizeof(unique_words)/1024))
    print('________________________________________________________________\n')
    return len(unique_words)

def python_numpy_unique(db, words):
    print('Standart python functionality (numpy.unique())')
    # unique_words = []
    collection = db.python_numpy_unique
    collection.delete_many({})

    start = time.time()
    for word in words:
        unique_words = [elem['word'] for elem in collection.find()]
        len_unique_words = len(unique_words)
        unique_words = np.unique(np.append(unique_words, word))
        if len(unique_words) > len_unique_words:
            collection.insert_one({'word': word})
        # unique_words = np.unique(unique_words.append(word))
    end = time.time()
    
    print('[python np.unique()] Time python:: {}'.format(end - start))
    print('[python np.unique()] Number of unique words: {}'.format(collection.count_documents({})))
    print('[python np.unique()] Size of unique words: {} Mb, {} Kb\n'.format(asizeof.asizeof(unique_words)/1024/1024, asizeof.asizeof(unique_words)/1024))
    print('________________________________________________________________\n')

def python_basic_in(db, words):
    print('Standart python functionality (word in list)')
    collection = db.python_basic_in
    collection.delete_many({})

    start = time.time()
    for word in words:
        unique_words = [elem['word'] for elem in collection.find()]
        if word not in unique_words:
            collection.insert_one({'word': word})
    end = time.time()

    print('[python] Time python: {}'.format(end - start))
    print('[python] python Number of words: {}'.format(collection.count_documents({})))
    print('[python] Size of unique_words: {} Mb, {} Kb'.format(asizeof.asizeof(unique_words)/1024/1024, asizeof.asizeof(unique_words)/1024))
    print('________________________________________________________________\n')

def datasketch_hllpp(db, words, unique_words_len, p):
    print('Datasketch Module: HLL++ __________ p = {}'.format(p))
    hpp = HyperLogLogPlusPlus(p=p)
    # unique_words = np.array([])
    # unique_words = []
    collection = db.datasketch_hllpp
    collection.delete_many({})

    start = time.time()
    for word in words:
        # Digest the hash object to get the hash value
        hv = hpp.hashfunc(word.encode('utf8'))
        # Get the index of the register using the first p bits of the hash
        reg_index = hv & (hpp.m - 1)
        # If hash not 0, word is unique
        if not hpp.reg[reg_index]:
            # unique_words = np.append(unique_words, word)
            collection.insert_one({'word': word})
        # Get the rest of the hash
        bits = hv >> hpp.p
        # Update the register
        hpp.reg[reg_index] = max(hpp.reg[reg_index], hpp._get_rank(bits))
    end = time.time()

    # count = hpp.count()
    count = collection.count_documents({})
    print('[datasketch HLL++] Time HLL: {}'.format(end - start))
    print('[datasketch HLL++] HLL Number of words: {}'.format(count))
    print('[datasketch HLL++] HLL counting error: {}%'.format(round((float(count)/unique_words_len)*100 - 100, 2)))
    size_hll = asizeof.asizeof(hpp)
    # size_hll_words = asizeof.asizeof(unique_words)
    print('[datasketch HLL++] Size of HLL++: {} Mb, {} Kb'.format(size_hll/1024/1024, size_hll/1024))
    # print('[datasketch HLL++] Size of array in HLL++: {} Mb, {} Kb'.format(size_hll_words/1024/1024, size_hll_words/1024))
    # print('[datasketch HLL++] Size of HLL++ total: {} Mb, {} Kb'.format((size_hll+size_hll_words)/1024/1024, (size_hll+size_hll_words)/1024))
    print('________________________________________________________________\n')

if __name__ == '__main__':
    client = pymongo.MongoClient('localhost', 27017)
    db = client.unique_words
    words, unique_words_len  = words_generator(100000)
    # python_set(db, words)
    # python_numpy_unique(db, words)
    datasketch_hllpp(db, words, unique_words_len, 12)
    # python_basic_in(db, words)
