FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app/
WORKDIR /usr/src/app/
ADD requirements.txt /my_app_dir/


RUN pip install — upgrade pip && pip install -r 
ADD . /usr/src/app/

VOLUME /usr/src/app/volume

