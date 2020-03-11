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

RUN apt-get install -y python2.7 python-pip
RUN pip install requests

RUN mkdir /client
COPY *.py /client/

RUN mkdir /docking
COPY docking /docking

RUN ls /docking

#RUN cd /docking ; python2.7 /client/docking.py

#RUN cd /client ; python2.7 getjob.py

#CMD /bin/sh

RUN apt-get install -y git

RUN cd /client/ ; git clone https://github.com/ccsb-scripps/AutoDock-GPU ; cd AutoDock-GPU ; make DEVICE=GPU NUMWI=32


#RUN cd /docking ; python2.7 /client/docking.py


