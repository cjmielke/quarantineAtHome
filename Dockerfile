FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y wget build-essential 


RUN wget http://autodock.scripps.edu/downloads/autodock-registration/tars/dist426/autodocksuite-4.2.6-src.tar.gz
RUN mkdir /autodock
RUN cd /autodock ; tar -xvzf /autodocksuite-4.2.6-src.tar.gz

RUN ls /autodock

RUN apt-get install -y csh

RUN cd /autodock/src/autogrid/ ; ./configure ; make ; make install

RUN cd /autodock/src/autodock/ ; ./configure ; make ; make install

RUN mkdir /client
COPY *.py /client

RUN apt-get install -y python2.7 python-pip
RUN pip install requests

RUN cd /client ; python2.7 getjob.py




