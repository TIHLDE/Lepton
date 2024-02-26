.DEFAULT_GOAL := help

.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: start
start: ## Start the webserver with docker on http://localhost:8000
	docker compose up

.PHONY: down
down: ## Take down server
	docker compose down -v

.PHONY: restart
restart: ## Rebuild and start the server
	docker compose build
	make start

.PHONY: fresh
fresh: ## Perform a fresh build, install and start the server
	docker compose build
	make makemigrations
	make migrate
	make loaddata
	make start


.PHONY: createsuperuser
createsuperuser: ## Create a new django superuser
	docker compose run --rm web python manage.py createsuperuser


.PHONY: makemigrations
makemigrations: ## Create migration files
	docker compose run --rm web python manage.py makemigrations

.PHONY: migrate
migrate: ## Run django migrations
	docker compose run --rm web python manage.py migrate ${args}

.PHONY: migrations
migrations: ## Create migration-files and migrate immediately
	make makemigrations
	make migrate

.PHONY: dumpdata
dumpdata: ## Dump current data stored into ./app/fixture.json
	docker compose run --rm web python manage.py dumpdata -e admin -e auth.Permission -e contenttypes --indent=4 > ./app/fixture.json

.PHONY: loaddata
loaddata: ## Load fixtures from ./app/fixture.json into the database
	docker compose run --rm web python manage.py loaddata ./app/fixture.json

.PHONY: collectstatic
collectstatic: ## Collect static files to a single location to be served in production
	docker compose run --rm web python manage.py collectstatic

.PHONY: test
test: ## Run test suite
	docker compose run --rm web pytest ${args}

.PHONY: cov
cov: ## Check test coverage
	docker compose run --rm web pytest --cov-config=.coveragerc --cov=app

.PHONY: format
format: ## Format code and imports
	make black
	make isort

.PHONY: check
check: ## Check formatting, imports and linting
	make black args="--check"
	make isort args="--check-only"
	make flake8

.PHONY: black
black: ## Format code only
	docker compose run --rm web black app/ ${args} --exclude migrations

.PHONY: isort
isort: ## Format imports only
	docker compose run --rm web isort . ${args}

.PHONY: flake8
flake8: ## Fheck code style
	docker compose run --rm web flake8 app

.PHONY: pr
pr: ## Pull Request format and checks
	make format
	git add .
	make check
	make test

.PHONY: shell
shell: ## Open an interactive Django shell
	docker compose run --rm web python manage.py shell
