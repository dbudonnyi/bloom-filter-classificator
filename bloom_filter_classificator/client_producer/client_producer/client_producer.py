from kafka import KafkaProducer, TopicPartition
from kafka.partitioner import RoundRobinPartitioner
import os
import socket
import logging
import time

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s')
KAFKA_TOPIC = 'bloom_topic'
KAFKA_CLIENT_IP = '192.168.1.104:9092'#.format(socket.gethostbyname(socket.gethostname()))


class ClientBloomClassificator():
    def __init__(self):
        partitioner = RoundRobinPartitioner(partitions=[
                                                TopicPartition(topic=KAFKA_TOPIC, partition=0),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=1),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=2),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=3),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=4),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=5),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=6),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=7),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=8),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=9),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=10),
                                                TopicPartition(topic=KAFKA_TOPIC, partition=11)
                                            ])
        self.kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_CLIENT_IP, partitioner=partitioner)

    def send_text(self, path_to_file):
        with open(path_to_file, errors='ignore') as f:
            text = " ".join(f.readlines())
        self.kafka_producer.flush()
        self.kafka_producer.send(KAFKA_TOPIC, text.encode('utf-8')).get(timeout=2)
        print("[{}] {}".format(time.time(), os.path.basename(path_to_file)))

    def end(self):
        self.kafka_producer.close()


if __name__ == '__main__':
    client = ClientBloomClassificator()
    time.sleep(20)
    i = 1
    while i<=1500:
        for file in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texts_to_classify')):
            print("Text #{}".format(i))
            client.send_text(os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts_to_classify", file))
            i+=1
    
