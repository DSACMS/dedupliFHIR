import json
import sys

import dedupe


def get_patient(entry):
    if entry["resource"]["resourceType"] != "Patient":
        return

    resource = entry["resource"]
    patient = {
        "id": resource["id"],
        "family_name": resource["name"][0]["family"],
        "given_name": " ".join(resource["name"][0]["given"]),
        "gender": resource["gender"],
        "birth_date": resource["birthDate"],
        "phone": "",
        "street_address": "",
        "city": "",
        "state": "",
        "postal_code": "",
    }
    # TODO: Handle multiple phones?
    if len(resource["telecom"]) > 0:
        patient["phone"] = resource["telecom"][0]["value"]

    # TODO: multiple addresses
    if len(resource["address"]) > 0:
        patient["street_address"] = " ".join(resource["address"][0]["line"])
        patient["city"] = resource["address"][0]["city"]
        patient["state"] = resource["address"][0]["state"]
        patient["postal_code"] = resource["address"][0].get("postalCode")

    return patient


def prepare_patient_data(fhir_data):
    patients = {}
    for idx, entry in enumerate(fhir_data["entry"]):
        patient = get_patient(entry)
        if patient:
            patients[f"{idx}"] = patient
    return patients


if __name__ == "__main__":
    json_data_str = sys.stdin.read()
    fhir_data = json.loads(json_data_str)

    patient_data = prepare_patient_data(fhir_data)

    dedupe_vars = [
        {"field": "family_name", "type": "String"},
        {"field": "family_name", "type": "Exact"},
        {"field": "given_name", "type": "String"},
        {"field": "gender", "type": "String"},
        {"field": "gender", "type": "Exact"},
        {"field": "birth_date", "type": "ShortString"},  # TODO:
        {"field": "phone", "type": "ShortString"},
        {"field": "street_address", "type": "String"},
        {"field": "city", "type": "String"},
        {"field": "state", "type": "ShortString"},
        {"field": "postal_code", "type": "ShortString"},
    ]

    training_data = dedupe.training_data_dedupe(patient_data, "id", 10)

    deduper = dedupe.Dedupe(dedupe_vars, num_cores=5)
    deduper.prepare_training(patient_data, sample_size=10)
    deduper.mark_pairs(training_data)
    deduper.train(index_predicates=True)
    output = deduper.partition(patient_data, threshold=0.5)
    breakpoint()
