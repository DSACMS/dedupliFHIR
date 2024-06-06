"""
This module defines the pytest testing functions and fixtures needed to test the 
de-dupliFHIR project.
"""
from pathlib import Path
import pytest
import pandas as pd
from io import StringIO
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
    generate_dup_data(column_path, csv_path, 800, 0.70)

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

    return clusters.as_pandas_dataframe()

@pytest.fixture
def dedup_test_data():
    test_data_csv = """id,truth_value,family_name,given_name,gender,birth_date,phone,street_address,city,state,postal_code,SSN
    "4_Arlene_Oliver.xml","","oliver","arlene","female","05/26/1972","434-228-8487","845 Collier Pike Center","North Katheryn","WA","99033",""
    "21_Raul_Waters.xml","","waters","raul","male","10/31/1972","(878)360-4765","61035 Adell Ranch Wall","Kerlukeburgh","NC","28885",""
    "22_Raul_Waters.xml","","waters","raul","male","10/31/1972","(878)360-4765","61035 Adell Ranch Wall","Kerlukeburgh","NC","28885",""
    "29_Terrance_Weber.xml","","weber","terrance","male","09/19/1960","903-814-2082","88790 Lemke Trail Road","South Quinton","NE","68843",""
    "30_Terrance_Weber.xml","","weber","terrance","male","09/12/1960","903-814-2082","88790 Lemke Trail Road","South Quinton","NE","68843",""
    """
    df = pd.read_csv(StringIO(test_data_csv))
    return df

def test_if_deduped_data_is_present(test_generate_data_and_dedup):
    """
    Test to make sure that data is returned from the Splink dedupe algorithm.
    """
    assert len(test_generate_data_and_dedup) != 0

def test_number_of_duplicates(test_generate_data_and_dedup):
    """
    Test to check if the expected number of duplicates is identified.
    """
    # Assuming 30% duplicates, calculate the expected number
    expected_duplicates = 800 * 0.30
    unique_clusters = test_generate_data_and_dedup['cluster_id'].nunique()
    
    assert (800 - unique_clusters) >= expected_duplicates * 0.9  # Allowing some tolerance

def test_deduplication_accuracy(test_generate_data_and_dedup):
    """
    Validate the accuracy of the deduplication by checking a few sample records.
    """
    df = test_generate_data_and_dedup
    duplicates = df[df.duplicated(subset=['given_name', 'family_name', 'birth_date'], keep=False)]
    
    # Check if duplicates are correctly identified
    assert len(duplicates) > 0
    assert duplicates['cluster_id'].nunique() < len(duplicates)

def test_no_records_lost(test_generate_data_and_dedup):
    """
    Ensure no records are lost in the deduplication process.
    """
    original_count = 800
    deduped_count = test_generate_data_and_dedup.shape[0]
    
    assert original_count == deduped_count

@pytest.mark.parametrize("data_size, duplicate_percentage", [
    (100, 0.10),
    (500, 0.25),
    (1000, 0.50)
])
def test_with_different_data_sizes(data_size, duplicate_percentage):
    """
    Test the deduplication process with different data sizes and percentages of duplicates.
    """
    test_path = (Path(__file__).parent).resolve()
    csv_path = str(test_path) + "/test_data.csv"
    column_path = str(test_path) + "/test_data_columns.json"

    #
    generate_dup_data(column_path, csv_path, data_size, duplicate_percentage)
    df = parse_test_data(csv_path)

    linker = DuckDBLinker(df, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)

    blocking_rule_for_training = block_on(["street_address", "postal_code"])

    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    blocking_rule_for_training = block_on("substr(birth_date, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    pairwise_predictions = linker.predict()

    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)

    deduped_df = clusters.as_pandas_dataframe()

    # Assertions
    assert len(deduped_df) != 0
    assert deduped_df.shape[0] == data_size
    unique_clusters = deduped_df['cluster_id'].nunique()
    expected_duplicates = data_size * duplicate_percentage
    assert (data_size - unique_clusters) >= expected_duplicates * 0.9  # Allowing some tolerance

def test_deduplicate_with_provided_data(dedup_test_data):
    """
    Test the deduplication process with provided test data.
    """
    df = dedup_test_data

    # Initialize Splink linker with test data
    linker = DuckDBLinker(df, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)

    # Blocking rule based on names
    blocking_rule_for_training = block_on(["given_name", "family_name"])

    # Estimate parameters using expectation maximisation
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    # Further blocking on birth year
    blocking_rule_for_training = block_on("substr(birth_date, 1, 4)")
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    # Generate pairwise predictions
    pairwise_predictions = linker.predict()

    # Cluster pairwise predictions
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)

    deduped_df = clusters.as_pandas_dataframe()

    # Assertions
    assert len(deduped_df) != 0

    # Check if duplicates are correctly identified
    # Raul Waters and Terrance Weber have duplicates
    duplicate_groups = deduped_df.groupby('cluster_id').size()
    duplicate_groups = duplicate_groups[duplicate_groups > 1]
    
    # We expect 2 duplicate clusters (Raul Waters and Terrance Weber)
    assert len(duplicate_groups) == 2

    # Check that the duplicates are correctly identified
    assert all(deduped_df[deduped_df['cluster_id'].isin(duplicate_groups.index)]['given_name'].isin(['raul', 'terrance']))

    # Ensure that non-duplicate records (Arlene Oliver) are not falsely identified as duplicates
    arlene_oliver_cluster = deduped_df[deduped_df['given_name'] == 'arlene']['cluster_id'].unique()
    assert len(arlene_oliver_cluster) == 1
    assert deduped_df[deduped_df['cluster_id'] == arlene_oliver_cluster[0]].shape[0] == 1
