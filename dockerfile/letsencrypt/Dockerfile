FROM ubuntu:16.04
MAINTAINER Marc-Andre Lemburg <mal@egenix.com>

# Set env vars
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Update system
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install make curl

# Add Let's Encrypt tool
RUN mkdir -p /usr/src/letsencrypt
COPY Makefile /usr/src/letsencrypt

# Setup runtime environment
ENV WORKDIR /home/letsencrypt
RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR
RUN ln -sf /usr/src/letsencrypt/Makefile .
