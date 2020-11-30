FROM ubuntu:20.04
COPY . /liberty
WORKDIR /liberty
RUN apt-get update && apt-get install -y python3 python3-dev python3-pip libopus0 ffmpeg
RUN pip3 install -r requirements.txt
CMD python3 ./liberty/bot.py
