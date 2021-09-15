FROM arm64v8/python:3.6
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # mysqlclient dependencies
  && apt-get install -y default-libmysqlclient-dev \
  && apt-get install -y libffi-dev libheif-dev libde265-dev \
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

VOLUME /usr/src/app/volume

EXPOSE 8000

CMD python manage.py collectstatic --noinput && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
