## Start the webserver with docker on http://localhost:8000
docker-compose = docker-compose run web python manage.py

## TODO: fix issue with pipenv not starting
makemigrations:
	$(docker-compose) showmigrations
	$(docker-compose) makemigrations ${app-label} --name ${name}

migrate:
	$(docker-compose) migrate

start:
	docker-compose up

start-fresh:
	docker-compose down
	docker-compose up --build
	make makemigrations
	make migrate
	make start
