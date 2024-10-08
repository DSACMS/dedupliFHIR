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
with open(os.path.join(dir_path,'splink_settings.json'),"r",encoding="utf-8") as f:
    splink_settings_dict = json.load(f)


#apply blocking function to translate into sql rules
BLOCKING_RULE_STRINGS = splink_settings_dict["blocking_rules_to_generate_predictions"]
#blocking_rules = list(
#    map(block_on,blocking_rules))

def get_additional_comparison_rules(parsed_data_df):
    """
    This function generates appropriate comparison rules based on pandas column names

    Arguments:
        parsed_data_df: The dataframe that was parsed from the user that we want to
        find duplicates in
    
    Returns:
        A generator collection object full of splink comparison objects
    """

    parsed_data_columns = parsed_data_df.columns

    for col in parsed_data_columns:
        if 'street_address' in col:
            yield cl.ExactMatch(col)
        elif 'postal_code' in col:
            yield cl.PostcodeComparison(col)

def create_blocking_rules():
    blocking_rules = []
    for rule in BLOCKING_RULE_STRINGS:
        if isinstance(rule, list):
            blocking_rules.append(block_on(*rule))
        else:
            blocking_rules.append(block_on(rule))
    
    return blocking_rules


def create_settings(parsed_data_df):
    """
    This function generates a Splink SettingsCreator object based on the parsed
    input data's columns and the blocking settings in splink_settings.json

    Arguments:
        parsed_data_df: The dataframe that was parsed from the user that we want to
        find duplicates in
    
    Returns:
        A splink SettingsCreator object to be used with a splink linker object
    """

    blocking_rules = create_blocking_rules()

    comparison_rules = [item for item in get_additional_comparison_rules(parsed_data_df)]
    comparison_rules.extend([
        cl.ExactMatch("phone").configure(
            term_frequency_adjustments=True
        ),
        cl.NameComparison("given_name").configure(
            term_frequency_adjustments=True
        ),
        cl.NameComparison("family_name").configure(
            term_frequency_adjustments=True
        ),
        cl.DateOfBirthComparison("birth_date",input_is_string=True)]
    )


    return SettingsCreator(
        link_type=splink_settings_dict["link_type"],
        blocking_rules_to_generate_predictions=blocking_rules,
        comparisons=comparison_rules,
        max_iterations=splink_settings_dict["max_iterations"],
        em_convergence=splink_settings_dict["em_convergence"])



def parse_fhir_dates(fhir_json_obj):
    """
    A generator function that parses the address portion of a FHIR file
    into a dictionary object that can be added to the overall patient record

    Arguments:
        fhir_json_obj: The object that has been parsed from the FHIR data
    
    Returns:
        A generator containing dictionaries of address data.
    """
    addresses = fhir_json_obj['entry'][0]['resource']['address']

    for addr,n in enumerate(sorted(addresses)):
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
        patient_dict["middle_name"] = [
            normalize_name_text(patient_json_record['entry'][0]['resouce']['name'][0]['given'][1])
        ]
    except IndexError:
        patient_dict["middle_name"] = [""]
        print("no middle name found!")

    for date in parse_fhir_dates(patient_json_record):
        patient_dict.update(date)

    return pd.DataFrame(patient_dict)
