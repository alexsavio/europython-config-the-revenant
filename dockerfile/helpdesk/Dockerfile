FROM python:2.7.9

RUN apt-get -y update
RUN apt-get install -y -q git
RUN mkdir -p /usr/src/helpdesk

WORKDIR /usr/src/helpdesk

RUN git clone https://github.com/EuroPython/ep-helpdesk.git .
RUN pip install -r requirements.txt
RUN mkdir -p /var/log/helpdesk
