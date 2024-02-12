.PHONY:
install:
	poetry install

test:
	cd cli; poetry run python -m pytest deduplifhirLib/tests.py
