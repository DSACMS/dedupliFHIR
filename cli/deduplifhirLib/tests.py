"""
This module defines the pytest testing functions and fixtures needed to test the 
de-dupliFHIR project.
"""
from pathlib import Path
import pytest
from splink.duckdb.linker import DuckDBLinker
from splink.duckdb.blocking_rule_library import block_on
from deduplifhirLib.duplicate_data_generator import generate_dup_data
from deduplifhirLib.settings import SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE
from deduplifhirLib.utils import parse_test_data


@pytest.fixture
def test_generate_data_and_dedup():
    """
    This test fixture uses Faker to generate a fresh set of patient records in a CSV.
    Then, it runs the Splink dedupe algorithm on the resulting pandas dataframe with 
    pre-generated duplicates.

    Returns:
        Dataframe containing deduped test data
    """

    test_path = (Path(__file__).parent).resolve()
    print(test_path)

    csv_path = str(test_path) + "/test_data.csv"
    column_path = str(test_path) + "/test_data_columns.json"

    #Create test data
    generate_dup_data(column_path, csv_path, 10000, 0.70)

    df = parse_test_data(csv_path)

    linker = DuckDBLinker(df, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)

    blocking_rule_for_training = block_on(["given_name", "family_name"])

    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    blocking_rule_for_training = block_on("substr(birth_date, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)


    pairwise_predictions = linker.predict()

    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)

    #clusters.as_pandas_dataframe().to_csv(csv_path)
    return clusters.as_pandas_dataframe()

def test_if_deduped_data_is_present(test_generate_data_and_dedup):
    """
    Test to make sure that data is returned from the Splink dedupe algorithm.
    """
    assert len(test_generate_data_and_dedup) != 0
