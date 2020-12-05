FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
COPY . /liberty
WORKDIR /liberty
RUN apt-get update && apt-get install -y python3 python3-dev python3-pip libopus0 ffmpeg
RUN pip3 install -r requirements.txt
WORKDIR ./liberty
CMD python3 ./bot.py
