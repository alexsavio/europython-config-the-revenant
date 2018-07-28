# Docker file for EP2016 python container
FROM python:2.7.9

# Upgrade System:
RUN apt-get update && apt-get -y upgrade && apt-get -y autoremove

# Download and install dependencies
RUN apt-get -y install -qq build-essential libssl-dev libxrender-dev wget git wkhtmltopdf

#Our Docker commands:
RUN mkdir -p /usr/src/ep2016
WORKDIR /usr/src/ep2016

RUN git clone -b ep2016 https://github.com/EuroPython/epcon.git .
RUN pip install -r requirements.txt
RUN pip install greenlet  # Required for both
RUN pip install eventlet  # For eventlet workers
RUN pip install gevent    # For gevent workers

