.PHONY:
install:
	poetry install

.PHONY:
start:
	poetry run flask --app app/__init__.py --debug run
