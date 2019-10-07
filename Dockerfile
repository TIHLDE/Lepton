FROM python:3.6.6-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src

# Install required packages for mysqlclient to work
RUN apk add --no-cache bash postgresql-dev postgresql-client mariadb-dev \
  mariadb-client python3-dev build-base
RUN apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers

# Copy over the source

COPY . .

RUN pip install --upgrade pip && pip install pipenv
RUN pipenv install

# Remove dependencies that are no longer needed.
RUN apk del .build-deps

VOLUME /usr/src/app/volume

CMD ./manage.py collectstatic --noinput && \
  gnuicorn -w 3 --bind 0.0.0.0:8000 --acess-logfile - app.wsgi:application
