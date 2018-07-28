# Docker file for EP2017 python container
FROM python:2.7.9

# Upgrade System:
RUN apt-get update && apt-get -y upgrade && apt-get -y autoremove

# Download and install dependencies
RUN apt-get install -qq build-essential libssl-dev libxrender-dev wget git wkhtmltopdf

#Our Docker commands:
RUN mkdir -p /usr/src/ep2018
WORKDIR /usr/src/ep2018

RUN git clone -b ep2018 https://github.com/EuroPython/epcon.git .
RUN pip install -r requirements.txt
RUN pip install greenlet  # Required for both
RUN pip install eventlet  # For eventlet workers
RUN pip install gevent    # For gevent workers

