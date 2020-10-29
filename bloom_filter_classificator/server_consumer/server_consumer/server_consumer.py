from kafka import KafkaConsumer
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from bloom_filter_classificator import BloomClassificator
import logging
import os
import socket
import time

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s')
KAFKA_TOPIC = 'bloom_topic'
KAFKA_CLIENT_IP = '172.20.10.3:9092'#.format(socket.gethostbyname(socket.gethostname()))
KAFKA_AUTO_OFFSET_RESET = 'earliest'


class ServerBloomClassificator():
    def __init__(self, dict_of_classes_with_training_files, additional_training=True, weight_of_text_to_train=0.7, weight_of_word_to_train=0.005):
        self.additional_training = additional_training
        self.weight_of_text_to_train = weight_of_text_to_train
        self.weight_of_word_to_train = weight_of_word_to_train
        self.bloom_classificator = BloomClassificator(dict_of_classes_with_training_files)
        self.kafka_consumer = KafkaConsumer(KAFKA_TOPIC, 
                                            bootstrap_servers=KAFKA_CLIENT_IP,
                                            group_id='1',
                                            partition_assignment_strategy=[RoundRobinPartitionAssignor])
        self.num_of_messages = 0

    def classify(self):
        for message in self.kafka_consumer:
            self.num_of_messages += 1
            print('[{}] Kafka - number in queue: {}, partition {}'.format(time.time(), message.offset, message.partition))
            self.bloom_classificator.classification(message.value.decode('utf-8'), 
                                                    additional_training=self.additional_training, 
                                                    weight_of_text_to_train=self.weight_of_text_to_train, 
                                                    weight_of_word_to_train=self.weight_of_word_to_train)
            print('[{}] Server - number of message: {}'.format(time.time(), self.num_of_messages))


if __name__ == '__main__':
    dict_of_classes_with_training_files = {}
    dict_of_classes_with_training_files['Football'] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_football', text) for text in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_football'))]
    dict_of_classes_with_training_files['Basketball'] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_basketball', text) for text in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_basketball'))]
    dict_of_classes_with_training_files['Traveling'] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_travel', text) for text in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training_travel'))]

    server_bloom_classificator = ServerBloomClassificator(dict_of_classes_with_training_files)
    while True:
        try:
            server_bloom_classificator.classify()
        except Exception as e:
            logging.error(e)
