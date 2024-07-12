"""
Below is the definition of the settings for the splink linker object

These settings control the way that spink trains its model in order to
find duplicates.

The blocking rules determine the preliminary records to match to each other in 
order to train the model, for this to work the data needs a couple records with the
same first and last name in the input in order to find confirmed matches 

The comparisons list defines the way the model will compare the data in order to find
the probability that records are duplicates of each other. 
"""
import os
import json
import uuid
import pandas as pd
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on


dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/splink_settings.json',"r",encoding="utf-8") as f:
    SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE = json.load(f)
from deduplifhirLib.normalization import normalize_addr_text, normalize_name_text


SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE.update({
    "comparisons": [
        ctl.name_comparison("given_name", term_frequency_adjustments=True),
        ctl.name_comparison("family_name", term_frequency_adjustments=True),
        ctl.date_comparison("birth_date", cast_strings_to_date=True, invalid_dates_as_null=True),
        ctl.postcode_comparison("postal_code"),
        cl.exact_match("street_address", term_frequency_adjustments=True),
        cl.exact_match("phone",  term_frequency_adjustments=True),
    ]
})

#apply blocking function to translate into sql rules
blocking_rules = SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE["blocking_rules_to_generate_predictions"]
BLOCKING_RULE_STRINGS = blocking_rules
SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE["blocking_rules_to_generate_predictions"] = list(
    map(block_on,blocking_rules))


#NOTE: The only reason this function is defined outside utils.py is because of a known bug with
#python multiprocessing: https://bugs.python.org/issue25053
def read_fhir_data(patient_record_path):
    """
    This function reads fhir data for a single patient and expresses the record as a dataframe
    with one record.

    Arguments:
        patient_record_path: The path to a single FHIR patient record, a JSON file.
    
    Returns:
        A dataframe holding FHIR data for a single patient.
    """
    try:
        with open(patient_record_path, "r", encoding="utf-8") as fdesc:
            patient_json_record = json.load(fdesc)
    except Exception as e:
        print(e)
        print(f"File: {patient_record_path}")
        raise e

    patient_dict = {
        "unique_id": uuid.uuid4().int,
        "family_name": [
            normalize_name_text(patient_json_record['entry'][0]['resource']['name'][0]['family'])
        ],
        "given_name": [
            normalize_name_text(patient_json_record['entry'][0]['resource']['name'][0]['given'][0])
        ],
        "gender": [patient_json_record['entry'][0]['resource']['gender']],
        "birth_date": patient_json_record['entry'][0]['resource']['birthDate'],
        "phone": [patient_json_record['entry'][0]['resource']['telecom'][0]['value']],
        "street_address": [
            normalize_addr_text(
                patient_json_record['entry'][0]['resource']['address'][0]['line'][0]
            )
        ],
        "city": [
            normalize_addr_text(patient_json_record['entry'][0]['resource']['address'][0]['city'])
        ],
        "state": [
            normalize_addr_text(patient_json_record['entry'][0]['resource']['address'][0]['state'])
        ],
        "postal_code": [patient_json_record['entry'][0]['resource']['address'][0]['postalCode']],
        "ssn": [patient_json_record['entry'][0]['resource']['identifier'][1]['value']],
        "path": patient_record_path
    }
    #print(patient_dict)

    return pd.DataFrame(patient_dict)
