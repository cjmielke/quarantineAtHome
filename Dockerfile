FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y wget build-essential
# build fails unless these are separate apt-get installs - don't consolidate
RUN apt-get install -y git csh python2.7 python-pip
RUN pip install requests

#RUN mkdir /client

##### Install MGLtools, which provides some utility scripts we need for both CPU and GPU versions
##### Need mglTools for both CPU and GPU versions - could make this a base image

RUN wget http://mgltools.scripps.edu/downloads/downloads/tars/releases/REL1.5.6/mgltools_x86_64Linux2_1.5.6.tar.gz
RUN tar -xvzf mgltools_x86_64Linux2_1.5.6.tar.gz
#RUN mv mgltools_x86_64Linux2_1.5.6 /client

RUN wget http://autodock.scripps.edu/downloads/autodock-registration/tars/dist426/autodocksuite-4.2.6-src.tar.gz
RUN mkdir /autodock
RUN cd /autodock ; tar -xvzf /autodocksuite-4.2.6-src.tar.gz
RUN ls /autodock

RUN cd /autodock/src/autogrid/ ; ./configure ; make ; make install
RUN cd /autodock/src/autodock/ ; ./configure ; make ; make install


COPY *.py /
COPY *.sh /
COPY receptors /receptors
COPY .git /.git

#RUN mkdir /docking
#COPY docking /docking
#RUN ls /docking

#RUN cd /docking ; python2.7 /client/docking.py

#RUN cd /client ; python2.7 getjob.py

#CMD /bin/sh


#RUN cd /docking ; python2.7 /client/docking.py



RUN pwd
RUN ls
RUN ls /receptors

#RUN prepare_dpf4.py
#ENV PATH="/mgltools_x86_64Linux2_1.5.6/bin:${PATH}"
#RUN ./mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf.py -h

RUN /client.sh

#CMD /client/client.sh

