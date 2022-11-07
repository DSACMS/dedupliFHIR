import json
import os
import re
import unicodedata
from contextlib import contextmanager

import dedupe

from . import base_dir

DEDUPE_VARS = [
    {"field": "family_name", "type": "String"},
    {"field": "family_name", "type": "Exact"},
    {"field": "given_name", "type": "String"},
    {"field": "gender", "type": "String"},
    {"field": "gender", "type": "Exact"},
    {"field": "birth_date", "type": "ShortString"},  # TODO:
    {"field": "phone", "type": "ShortString"},
    {"field": "street_address", "type": "String", "has_missing": True},
    {"field": "city", "type": "String"},
    {"field": "state", "type": "ShortString"},
    {"field": "postal_code", "type": "ShortString"},
]


# https://github.com/dedupeio/dedupe-examples/blob/master/mysql_example/mysql_example.py


# TODO: Should this be a decorator?
@contextmanager
def use_deduper(*args, **kwargs):
    # TODO: should handle wrapping directory for storage, just needs slug
    # TODO: Take a name/slug (created from filename), load data including
    # settings/training if exist
    # args[0] is slug
    data_dir = os.path.join(base_dir, ".data", args[0])
    data_path = os.path.join(data_dir, "data.json")
    training_path = os.path.join(data_dir, "training.json")
    with open(data_path, "r") as f:
        dedupe_data = json.load(f)
    # TODO: Dynamically pull cores
    deduper = dedupe.Dedupe(DEDUPE_VARS, num_cores=4)
    if os.path.exists(training_path):
        with open(training_path, "r") as f:
            deduper.prepare_training(dedupe_data, training_file=f)
    else:
        deduper.prepare_training(dedupe_data)

    # https://github.com/dedupeio/dedupe/blob/main/dedupe/convenience.py#L123
    # TODO: Pull from this for an example
    # GET
    # deduper.uncertain_pairs(), pull record_pair from that
    # load from training pairs the number of same

    # POST
    # mark_pairs should be called from POST

    try:
        yield deduper
    finally:
        with open(training_path, "w") as f:
            deduper.write_training(f)
        # TODO: save settings?


# Pulled from Django
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower()).strip()
    return re.sub(r"[-\s]+", "-", value)


def get_slugs():
    slugs = []
    for list_path in os.listdir(os.path.join(base_dir, ".data")):
        if os.path.isdir(os.path.join(base_dir, ".data", list_path)):
            slugs.append(list_path)

    return slugs


def get_fhir_filename(slug):
    return os.path.join(
        base_dir,
        ".data",
        slug,
        "fhir",
        os.listdir(os.path.join(base_dir, ".data", slug, "fhir"))[0],
    )


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
