PYTHON ?= python
MANAGE ?= manage.py

.PHONY: help install migrate run test test-users compose-up compose-down start

help:
	@echo "Available commands:"
	@echo "  make install        - install Python dependencies"
	@echo "  make migrate        - apply database migrations"
	@echo "  make run            - start the Django development server"
	@echo "  make start          - build and start Docker Compose with local code mounted"
	@echo "  make compose-up     - build and start Docker Compose services"
	@echo "  make compose-dev    - build and start Docker Compose in local development mode"
	@echo "  make compose-down   - stop Docker Compose services"
	@echo "  make test           - run the full test suite"
	@echo "  make test-users     - run the users app tests"

install:
	$(PYTHON) -m pip install -r requirements.txt

migrate:
	$(PYTHON) $(MANAGE) migrate

run:
	$(PYTHON) $(MANAGE) runserver 0.0.0.0:8000

compose-up:
	docker compose up --build

compose-dev:
	docker compose up --build

start: compose-dev

compose-down:
	docker compose down

test:
	$(PYTHON) $(MANAGE) test

test-users:
	$(PYTHON) $(MANAGE) test users.tests
