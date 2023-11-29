import pytest
from pathlib import Path
from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from deduplifhirLib.duplicate_data_generator import generate_dup_data
from deduplifhirLib.settings import SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE, read_fhir_data
from deduplifhirLib.utils import parse_test_data

def test_generate_data_and_dedup():
    testPath = (Path(__file__).parent).resolve()
    print(testPath)

    csvPath = str(testPath) + "/test_data.csv"
    column_path = str(testPath) + "/test_data_columns.json"

    #Create test data
    generate_dup_data(column_path, csvPath, 10000, 0.70)

    df = parse_test_data(csvPath)

    linker = DuckDBLinker(df, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)
    
    blocking_rule_for_training = block_on(["given_name", "family_name"])
    
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    blocking_rule_for_training = block_on("substr(birth_date, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    
    pairwise_predictions = linker.predict()
    
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)
    
    #clusters.as_pandas_dataframe().to_csv(csvPath)
    print(clusters.as_pandas_dataframe())