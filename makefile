## Start the webserver with docker on http://localhost:8000
start:
	docker-compose up

restart:
	docker-compose build
	docker-compose up

start-fresh:
	docker-compose build
	make makemigrations
	make migrate
	make loaddata
	docker-compose up

createsuperuser: ##@Docker Create a superuser
	docker-compose run --rm web pipenv run python manage.py createsuperuser

makemigrations: ##@Docker Set up migration files
	docker-compose run --rm web pipenv run python manage.py makemigrations

migrate: ##@Docker Perform migrations to database
	docker-compose run --rm web pipenv run python manage.py migrate

dumpdata:
	docker-compose run --rm web pipenv run python manage.py dumpdata > ./app/fixture.json

loaddata:
	docker-compose run --rm web pipenv run python manage.py loaddata ./app/fixture.json

test:
	docker-compose run web pipenv run python manage.py test

pytest:
	docker-compose run web pipenv run pytest
