.PHONY:
install:
	poetry install

test:
	cd cli; poetry run python -m pytest deduplifhirLib/tests.py

dist:
	./set-up-python-env.sh; cd frontend; electron-builder