FROM ubuntu:18.04

RUN apt-get update > /dev/null &&  apt-get -y -q install \
    python3-pip > /dev/null

RUN pip3 install kafka-python==1.4.4 pympler bloom_filter numpy stop_words nltk

RUN python3 -m nltk.downloader -d /usr/share/nltk_data punkt
RUN python3 -m nltk.downloader -d /usr/share/nltk_data stopwords
RUN python3 -m nltk.downloader -d /usr/share/nltk_data wordnet

CMD ["/usr/bin/python3", "/opt/server_consumer/server_consumer.py"]