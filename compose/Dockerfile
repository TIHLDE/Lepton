# Splits the Dockerfile into multiple stages.
# The `dev`-stage installs dependencies copies the required files, waits for the database connection
# and runs the server in "development-mode".
# Use --target=dev to only use this stage.
FROM python:3.6-slim-buster as dev
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # mysqlclient dependencies
  && apt-get install -y default-libmysqlclient-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

COPY ./compose/wait-for-mysql /wait-for-mysql
RUN sed -i 's/\r$//g' /wait-for-mysql
RUN chmod +x /wait-for-mysql

ENTRYPOINT [ "/wait-for-mysql" ]

VOLUME /usr/src/app/volume

EXPOSE 8000

CMD echo "Starting development-server" && \
    python manage.py runserver 0.0.0.0:8000

# The `prod`-stage uses the dev-files and installed dependencies.
# Then collects the static files and runs the db-migrations against the db.
# Then runs them in "production-mode" with Gunicorn and Uvicorn
FROM dev as prod

ENV PROD=True

COPY --from=dev /usr/src /usr/src

WORKDIR /usr/src

CMD echo "Starting production-server" && \
    python manage.py collectstatic --noinput && \
    python manage.py migrate && \
    # https://docs.gunicorn.org/en/stable/design.html#how-many-workers
    gunicorn --bind 0.0.0.0:8000 -w 3 -k app.uvicorn.UvicornWorker app.asgi:application
