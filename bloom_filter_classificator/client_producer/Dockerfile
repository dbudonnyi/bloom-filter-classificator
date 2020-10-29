FROM ubuntu:18.04

RUN apt-get update > /dev/null &&  apt-get -y -q install \
    python3-pip > /dev/null

RUN pip3 install kafka-python==1.4.4

CMD ["/usr/bin/python3", "/opt/client_producer/client_producer.py"]