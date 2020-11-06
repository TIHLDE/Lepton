FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv && \
    # Install required linux packages (remove postgresql-dev when Heroku isn't needed)
    apk add --no-cache mariadb-dev postgresql-dev

COPY Pipfile Pipfile.lock ./

# Install required python packages
RUN apk add --no-cache --virtual .build-deps gcc linux-headers libc-dev && \
      pipenv install -d && \
      rm -rf ~/.cache/pip ~/.cache/pipenv && \
    apk del .build-deps

COPY . .

VOLUME /usr/src/app/volume

CMD ./manage.py collectstatic --noinput && \
    gnuicorn -w 3 --bind 0.0.0.0:8000 --acess-logfile - app.wsgi:application
