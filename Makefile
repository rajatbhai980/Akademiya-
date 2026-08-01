PYTHON ?= env\Scripts\python.exe
MANAGE ?= manage.py

.PHONY: help install migrate run test test-users test-all

help:
	@echo "Available commands:"
	@echo "  make install        - install Python dependencies"
	@echo "  make migrate        - apply database migrations"
	@echo "  make run            - start the Django development server"
	@echo "  make test           - run the full test suite"
	@echo "  make test-users     - run the users app tests"

install:
	$(PYTHON) -m pip install -r requirements.txt

migrate:
	$(PYTHON) $(MANAGE) migrate

run:
	$(PYTHON) $(MANAGE) runserver 0.0.0.0:8000

test:
	$(PYTHON) $(MANAGE) test

test-users:
	$(PYTHON) $(MANAGE) test users.tests
