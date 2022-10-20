DEDUPE_FIELDS = family_name given_name gender birth_date phone street_address city state postal_code

all: output/reports.json

.PRECIOUS: input/patients.json input/measures.json

.PHONY:
install:
	poetry install
	npm install

output/reports.json: input/clean-patients.json input/measures.json
	npx fqm-execution reports -p $< -m $(filter $<,$^) > $@

input/clean-patients.json: input/clustered-mapping.csv input/patients.json
	poetry run python scripts/clean_patients.py $^ > $@

input/cluster-mapping.csv: input/clustered-patients.csv
	cat $< | poetry run python scripts/group_by_cluster.py > $@

# TODO: Pre-assign weights?
input/clustered-patients.csv: input/patients.csv
	poetry run python csvdedupe $< --field_names $(DEDUPE_FIELDS) --output_file $@

input/patients.csv: input/patients.json
	cat $< | poetry run python scripts/patient_fhir_to_csv.py > $@ 
