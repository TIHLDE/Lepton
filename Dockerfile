FROM python:3.6
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app/



RUN pip install — upgrade pip && pip install pipenv
RUN pipenv install
ADD . /usr/src/app/

VOLUME /usr/src/app/volume

