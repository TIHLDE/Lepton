FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src

RUN pip install --no-cache-dir --upgrade pip && \
    apk add --no-cache mariadb-dev

COPY requirements.txt ./

# Install required python packages
RUN apk --update add --no-cache --virtual .build-deps python3 cmake g++ gcc musl-dev python3-dev libffi-dev openssl-dev cargo py-pip linux-headers libc-dev build-base && \
      pip install --upgrade pip && \
      pip install -r requirements.txt && \
      rm -rf ~/.cache/pip && \
    apk del .build-deps

COPY . .

VOLUME /usr/src/app/volume

EXPOSE 8000

CMD python manage.py collectstatic --noinput && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
