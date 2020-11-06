help:
	@echo 'start                  - start the server'
	@echo 'restart                - rebuild and start the server'
	@echo 'fresh                  - perform a fresh build, install and start the server'
	@echo 'createsuperuser        - create a new django superuser'
	@echo 'makemigrations         - create migration files'
	@echo 'migrate                - run django migrations'
	@echo 'dumpdata               - dump current data stored into ./app/fixture.json'
	@echo 'loaddata               - load fixtures from ./app/fixture.json into the database'
	@echo 'collectstatic          - collect static files to a single location to be served in production'
	@echo 'test                   - run test suite'
	@echo 'format                 - format code and imports'
	@echo 'check                  - check formatting, imports and linting'
	@echo 'black                  - format code only'
	@echo 'isort                  - format imports only'
	@echo 'flake8                 - check code style'

## Start the webserver with docker on http://localhost:8000
start:
	docker-compose up

restart:
	docker-compose build
	docker-compose up

fresh:
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
	docker-compose run --rm web pipenv run python manage.py dumpdata -e admin -e auth.Permission -e contenttypes --indent=4 > ./app/fixture.json

loaddata:
	docker-compose run --rm web pipenv run python manage.py loaddata ./app/fixture.json

collectstatic:
	docker-compose run --rm web pipenv run python manage.py collectstatic

test:
	docker-compose run web pipenv run pytest ${args}

format:
	make black
	make isort

check:
	make black args="--check"
	make isort args="--check-only"
	make flake8

black:
	docker-compose run web pipenv run black app/ ${args} --exclude migrations

isort:
	docker-compose run web pipenv run isort . ${args}

flake8:
	docker-compose run web pipenv run flake8 app

PR:
	make format
	git add .
	make check
	make test