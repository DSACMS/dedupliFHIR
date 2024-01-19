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
import json
import uuid
import pandas as pd
from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from splink.datasets import splink_datasets


SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE = {
    "link_type": "dedupe_only",
    "blocking_rules_to_generate_predictions": [
        block_on("given_name"),
        block_on("family_name"),
    ],
    "comparisons": [
        ctl.name_comparison("given_name"),
        ctl.name_comparison("family_name"),
        ctl.date_comparison("birth_date", cast_strings_to_date=True),
        cl.exact_match("city", term_frequency_adjustments=True),
    ],
}



splink_test_df = splink_datasets.fake_1000

#This is the same as the above settings object, but for the test fake data.
SPLINK_LINKER_SETTINGS_TEST_DEDUPE = {
    "link_type": "dedupe_only",
    "blocking_rules_to_generate_predictions": [
        block_on("first_name"),
        block_on("surname"),
    ],
    "comparisons": [
        ctl.name_comparison("first_name"),
        ctl.name_comparison("surname"),
        ctl.date_comparison("dob", cast_strings_to_date=True),
        cl.exact_match("city", term_frequency_adjustments=True),
        ctl.email_comparison("email", include_username_fuzzy_level=False),
    ],
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
        with open(patient_record_path, "r") as f:
            patient_json_record = json.load(f)
    except Exception as e:
        print(e)
        print(f"File: {patient_record_path}")
        raise e

    patient_dict = {
        "unique_id": uuid.uuid4().int,
        "family_name": [patient_json_record['entry'][0]['resource']['name'][0]['family']],
        "given_name": [patient_json_record['entry'][0]['resource']['name'][0]['given'][0]],
        "gender": [patient_json_record['entry'][0]['resource']['gender']],
        "birth_date": patient_json_record['entry'][0]['resource']['birthDate'],
        "phone": [patient_json_record['entry'][0]['resource']['telecom'][0]['value']],
        "street_address": [patient_json_record['entry'][0]['resource']['address'][0]['line'][0]],
        "city": [patient_json_record['entry'][0]['resource']['address'][0]['city']],
        "state": [patient_json_record['entry'][0]['resource']['address'][0]['state']],
        "postal_code": [patient_json_record['entry'][0]['resource']['address'][0]['postalCode']],
        "ssn": [patient_json_record['entry'][0]['resource']['identifier'][1]['value']]
    }
    #print(patient_dict)

    return pd.DataFrame(patient_dict)


if __name__ == "__main__":
    #DuckDBLinker just defines the Pandas Dataframe format as using
    #DuckDB style formatting
    linker = DuckDBLinker(splink_test_df, SPLINK_LINKER_SETTINGS_TEST_DEDUPE)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)

    blocking_rule_for_training = block_on(["first_name", "surname"])

    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    blocking_rule_for_training = block_on("substr(dob, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)


    pairwise_predictions = linker.predict()

    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)

    print(clusters.as_pandas_dataframe(limit=25))
