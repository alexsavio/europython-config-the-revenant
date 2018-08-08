# Docker file for EP2017 python container
FROM python:2.7.9

ARG EPCON_BRANCH=ep2017

# Upgrade System:
RUN apt-get update && ⁠\
		apt-get -y upgrade && ⁠\
		apt-get -y autoremove

# Download and install dependencies
RUN apt-get -y install -qq build-essential libssl-dev libxrender-dev wget git wkhtmltopdf

#Our Docker commands:
RUN mkdir -p /usr/src/$EPCON_BRANCH
WORKDIR /usr/src/$EPCON_BRANCH

RUN git clone --depth=1 -b $EPCON_BRANCH https://github.com/EuroPython/epcon.git . && ⁠\
    pip install -r requirements.txt && ⁠\
    pip install greenlet && ⁠\
    pip install eventlet && ⁠\
    pip install gevent
