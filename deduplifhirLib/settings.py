from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from splink.datasets import splink_datasets
import json
import pandas as pd
import uuid

DEDUPE_VARS = [
    {"field": "family_name", "type": "String"},
    {"field": "family_name", "type": "Exact"},
    {"field": "given_name", "type": "String"},
    {"field": "gender", "type": "String"},
    {"field": "gender", "type": "Exact"},
    {"field": "birth_date", "type": "ShortString"},
    {"field": "phone", "type": "ShortString"},
    {"field": "street_address", "type": "String", "has_missing": True},
    {"field": "city", "type": "String"},
    {"field": "state", "type": "ShortString"},
    {"field": "postal_code", "type": "ShortString"},
]

settings = {
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

testSettings = {
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

def read_fhir_data(patient_record_path):
    try:
        with open(patient_record_path, "r") as f:
            patient_json_record = json.load(f)
    except Exception as e:
        print(e)
        print(f"File: {patient_record_path}")
        raise e
    
    patient_dict = {
        "unique_id": uuid.uuid4,
        "family_name": [patient_json_record['entry'][0]['resource']['name'][0]['family']],
        "given_name": [patient_json_record['entry'][0]['resource']['name'][0]['given'][0]],
        "gender": [patient_json_record['entry'][0]['resource']['gender']],
        "birth_date": patient_json_record['entry'][0]['resource']['birthDate'],
        "phone": [patient_json_record['entry'][0]['resource']['telecom'][0]['value']],
        "street_address": [patient_json_record['entry'][0]['resource']['address'][0]['line'][0]],
        "city": [patient_json_record['entry'][0]['resource']['address'][0]['city']],
        "state": [patient_json_record['entry'][0]['resource']['address'][0]['state']],
        "postal_code": [patient_json_record['entry'][0]['resource']['address'][0]['postalCode']]
    }
    #print(patient_dict)
    
    return pd.DataFrame(patient_dict)


if __name__ == "__main__":
    #DuckDBLinker just defines the Pandas Dataframe format as using
    #DuckDB style formatting
    linker = DuckDBLinker(splink_test_df, testSettings)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)
    
    blocking_rule_for_training = block_on(["first_name", "surname"])
    
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    blocking_rule_for_training = block_on("substr(dob, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    
    pairwise_predictions = linker.predict()
    
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)
    
    print(clusters.as_pandas_dataframe(limit=25))