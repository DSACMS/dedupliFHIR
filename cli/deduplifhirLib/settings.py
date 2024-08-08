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
import splink.comparison_library as cl
from splink import SettingsCreator, block_on
from deduplifhirLib.normalization import (
    normalize_addr_text, normalize_name_text, normalize_date_text
)


dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/splink_settings.json',"r",encoding="utf-8") as f:
    splink_settings_dict = json.load(f)


#apply blocking function to translate into sql rules
BLOCKING_RULE_STRINGS = splink_settings_dict["blocking_rules_to_generate_predictions"]
#blocking_rules = list(
#    map(block_on,blocking_rules))

blocking_rules = []
for rule in BLOCKING_RULE_STRINGS:
    if isinstance(rule, list):
        blocking_rules.append(block_on(*rule))
    else:
        blocking_rules.append(block_on(rule))


comparison_rules = [
    cl.ExactMatch("street_address0").configure(
        term_frequency_adjustments=True
    ),
    cl.ExactMatch("phone").configure(
        term_frequency_adjustments=True
    ),
    cl.NameComparison("given_name").configure(
        term_frequency_adjustments=True
    ),
    cl.NameComparison("family_name").configure(
        term_frequency_adjustments=True
    ),
    cl.DateOfBirthComparison("birth_date",input_is_string=True),
    cl.PostcodeComparison("postal_code0")
]


SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE = SettingsCreator(
    link_type=splink_settings_dict["link_type"],
    blocking_rules_to_generate_predictions=blocking_rules,
    comparisons=comparison_rules,
    max_iterations=splink_settings_dict["max_iterations"],
    em_convergence=splink_settings_dict["em_convergence"])



def parse_fhir_dates(fhir_json_obj):

    addresses = fhir_json_obj['entry'][0]['resource']['address']

    for addr,n in enumerate(addresses):
        yield {
            f"street_address{n}": [normalize_addr_text(''.join(addr['line']))],
            f"city{n}": [normalize_addr_text(addr['city'])],
            f"state{n}": [normalize_addr_text(addr['state'])],
            f"postal_code{n}": [normalize_addr_text(addr['postalCode'])]
        }





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
        "birth_date": normalize_date_text(
            patient_json_record['entry'][0]['resource']['birthDate']
        ),
        "phone": [patient_json_record['entry'][0]['resource']['telecom'][0]['value']],
        "ssn": [patient_json_record['entry'][0]['resource']['identifier'][1]['value']],
        "path": patient_record_path
    }

    try:
        patient_dict["middle_name"] = [normalize_name_text(patient_json_record['entry'][0]['resouce']['name'][0]['given'][1])]
    except IndexError:
        patient_dict["middle_name"] = [""]
        print("no middle name found!")
    
    for date in parse_fhir_dates(patient_json_record):
        patient_dict.update(date)

    return pd.DataFrame(patient_dict)
