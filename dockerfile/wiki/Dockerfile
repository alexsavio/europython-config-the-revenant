# Docker file for wiki python container
FROM python:2.7.9

# Upgrade System:
RUN apt-get update && apt-get -y upgrade && apt-get -y autoremove

# Download and install dependencies
RUN apt-get install -qq build-essential libssl-dev libxrender-dev wget git wkhtmltopdf

#Our Docker commands:
RUN mkdir -p /usr/src/wiki
WORKDIR /usr/src/wiki

RUN git clone https://github.com/EuroPython/ep-wiki.git .
RUN pip install -r requirements.txt
