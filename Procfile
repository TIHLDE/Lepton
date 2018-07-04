web: gunicorn config.wsgi:application
worker: celery worker --app=api.taskapp --loglevel=info
