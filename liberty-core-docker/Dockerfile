FROM ubuntu:20.04

LABEL version=1.0.0

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-dev python3-pip libopus0 ffmpeg
RUN pip3 install -r ../requirements.txt
