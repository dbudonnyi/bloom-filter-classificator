from monkeylearn import MonkeyLearn
import os
import time

ml = MonkeyLearn('046a67987f134e7a86fa5c17d05a5a3e9b62449d')
model_id = 'cl_BedHjRKG'
start_time = time.time()
for i, file in enumerate(os.listdir('texts_to_classify')):
    data = []
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts_to_classify", file), errors='ignore') as f:
        data.append(" ".join(f.readlines()))
    result = ml.classifiers.classify(model_id, data)
    tag = result.body[0]["classifications"][0]["tag_name"]
    # print('File: {}'.format(file.lower()))
    print('{}) Tag: {},\t result of classification - {}'.format(i + 1, tag, tag.lower() in file.lower()))
print("Time for classification: {}".format(time.time() - start_time))