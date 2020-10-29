
# Requirements
Docker installed on your machine

# How to start:
**1.** Clone git repository

**2.** Get IP of your machine. On Mac do next:
   * Go to System Preferences
   * Go to Network
   * Get the IP

**3.** Open terminal at dir _bloom_filter_classificator/kafka/_, then build and run kafka docker container using next commands:
```
docker build -t broker_kafka:1.0 .
docker run --rm -a STDIN -a STDOUT -a STDERR -p 2181:2181 -p 9092:9092 --env ADVERTISED_HOST=192.168.1.114 --env ADVERTISED_PORT=9092 --env CONSUMER_THREADS=2 --env NUM_PARTITIONS=2 --env AUTO_CREATE_TOPICS --env TOPICS=bloom_topic --env GROUP_ID=1 --name kafka broker_kafka:1.0
```
   **Note:** 
   * ADVERTISED_HOST - IP on your machine (will be the Kafka IP)
   * CONSUMER_THREADS - number of consumers
   * NUM_PARTITIONS - number of partitions per topic (should be the same as number of consumers as one consumer have to be per one partition)

**4.** Change IP of kafka container in producer and consumer scripts:
  * KAFKA_CLIENT_IP in the script *bloom_filter_classificator/server_consumer/server_consumer/server_consumer.py*
  * KAFKA_CLIENT_IP in the script *bloom_filter_classificator/client_producer/client_producer/client_producer.py*
  
**5.** To specify the number of messages to be sent by producer to kafka, change the number of messages in _while loop_ in the file *bloom_filter_classificator/client_producer/client_producer/client_producer.py*

**6.** Specify the correct number of consumers (partitions) in the file *bloom_filter_classificator/client_producer/client_producer/client_producer.py*. To do this just leave in the list of partitions the correct number of partions. You can just comment/uncomment TopicPartition in list. By default, 12 partions are enabled

**7.** In _bloom_filter_classificator/docker-compose.yml_ file change paths of volumes for server_consumer and client_producer to the correct dir path of project location

**8.** Open terminal at dir _bloom_filter_classificator/_ and run next command to build and run producers and consumers
```
docker-compose up --scale server_consumer=12 --scale client_producer=1
```
   **Note:** 
   * server_consumer - number of consumers (clasification servers)
   * client_producer - number of produces (client server, which send messages) 
