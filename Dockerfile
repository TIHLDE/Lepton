FROM python:3.6.6-alpine
ENV PYTHONUNBUFFERED 1

# Adds our application code to the image
COPY . /usr/src/app 
WORKDIR /usr/src/app 

# Install postgres bindings
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 apk add --no-cache mariadb-dev && \
 python3 -m pip install pipenv --no-cache-dir && \
 pipenv install --deploy --system --ignore-pipfile && \
 apk --purge del .build-deps

# expose
EXPOSE 8000


VOLUME /usr/src/app/volume

# # Migrates the database, uploads staticfiles, and runs the production server
CMD ./manage.py migrate && \
    ./manage.py collectstatic --noinput && \
    gunicorn -w 3 --bind 0.0.0.0:8000 --access-logfile - app.wsgi:application
