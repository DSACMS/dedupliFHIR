DEDUPE_FIELDS = family_name given_name gender birth_date phone street_address city state postal_code

all: output/reports.json

.PRECIOUS: input/patients.json input/measures.json

.PHONY:
install:
	poetry install

.PHONY:
start:
	poetry run flask --app app/__init__.py --debug run
