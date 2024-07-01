"""
This module defines pytest testing functions
and fixtures for testing the deduplication 
functionality using Splink.
"""

import os
import tempfile
from unittest.mock import patch
from io import StringIO
import pytest
import pandas as pd
from click.testing import CliRunner
from cli.deduplifhirLib.tests.duplicate_data_generator import generate_dup_data
from cli.ecqm_dedupe import dedupe_data



@pytest.fixture
def generate_mock_data_fixture(request):
    """
    Fixture to generate mock patient data using 
    generate_dup_data function with configurable 
    rows.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.close()
        generate_dup_data('deduplifhirLib/tests/test_data_columns.json',
         temp_file.name, rows=request.param, duprate=0.2)
        sample_df = pd.read_csv(temp_file.name)
        assert sample_df.shape[0] == request.param, f"Expected {request.param} deduplicated records"
        print(sample_df)
        yield temp_file.name
        os.remove(temp_file.name)


@pytest.fixture
def cli_runner():
    """
    Fixture to provide a CliRunner instance to invoke Click commands programmatically.
    """
    return CliRunner()

def test_dedupe_data_with_csv_output(cli_runner):
    """
    Test dedupe_data function with CSV output format.
    """

    # Prepare test data paths
    bad_data_path = 'deduplifhirLib/tests/test_data.csv'
    output_path = 'output.csv'
    print(os.getcwd())
    # Simulate CLI command execution
    result = cli_runner.invoke(dedupe_data, ['--fmt', 'CSV', bad_data_path, output_path])

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert os.path.exists(output_path), "Output file not created"

    # Check content of the output file (assuming it's CSV)
    deduped_df = pd.read_csv(output_path)
    assert 'cluster_id' in deduped_df.columns, "Expected column 'cluster_id' not found"

    # Clean up: delete output file
    os.remove(output_path)

def test_dedupe_data_with_specific_csv(cli_runner):
    """
    Test dedupe_data function with specific CSV data to verify deduplication.
    """
    # Prepare test data
    test_data_csv = """id,truth_value,family_name,given_name,gender,birth_date,phone,street_address,city,state,postal_code,SSN
8,9b0b0b7c-e05e-4c89-991d-268eab2483f7,Obrien,Curtis,M,07/02/1996,,300 Amy Corners Suite 735,Rileytown,Alaska,60281,480-21-0833
342,9b0b0b7c-e05e-4c89-991d-268eab2483f7,Orbien,Cutris,M,07/02/1996,,300 Amy oCrenrs Suite 735,Rileytown,Alaska,60281,480-210-833
502,9b0b0b7c-e05e-4c89-991d-268eab2483f7,bOrien,Curtsi,M,07/02/1996,,300 AmyCo rners Suite 735,Rileytown,Alaska,60281,480-21-8033
618,9b0b0b7c-e05e-4c89-991d-268eab2483f7,Obrine,Curtsi,M,07/02/1996,,300 AmyC orners Suite7 35,Rileytown,Alaska,60281,48-021-0833
744,9b0b0b7c-e05e-4c89-991d-268eab2483f7,bOrien,Curtsi,M,07/02/1996,,3 00Amy Corners Suite 735,Rileytown,Alaska,60281,480-210-833
223,04584982-ae7a-44a1-b4f0-e927a8bab0e1,Russell,Lindsay,F,02/05/1977,,2110 Kimberly Villages Apt. 639,New David,Wyoming,52082,211-52-6998
225,04584982-ae7a-44a1-b4f0-e927a8bab0e1,R,Lindsay,F,02/05/1977,,2110 Kimberly Villages Apt. 639,New David,Wyoming,52082,211-52-6998
226,04584982-ae7a-44a1-b4f0-e927a8bab0e1,Russel Smith,Lindsay,F,02/05/1977,,2110 Kimberly Villages Apt. 639,New David,Wyoming,52082,211-52-6998
273,04584982-ae7a-44a1-b4f0-e927a8bab0e1,Russlel,Lnidsay,F,02/05/1977,,2110 Kimbelry Vilalges Apt. 639,New David,Wyoming,52082,211-52-6989
311,04584982-ae7a-44a1-b4f0-e927a8bab0e1,Russlel,Lindasy,F,02/05/1977,,2110 Kimbelry Villgaes Apt. 639,New David,Wyoming,52082,211-52-9698
652,04584982-ae7a-44a1-b4f0-e927a8bab0e1,uRssell,Lidnsay,F,02/05/1977,,2110 Kimberly Vlilagse Apt. 639,New David,Wyoming,52082,121-52-6998
726,04584982-ae7a-44a1-b4f0-e927a8bab0e1,uRssell,Lindasy,F,02/05/1977,,2110 Kmiberly Vilalges Apt. 639,New David,Wyoming,52082,2115-2-6
    """

    # Write test data to specific.csv
    with open('specific.csv', 'w',encoding='utf-8') as f:
        f.write(test_data_csv)

    # Simulate CLI command execution

    result = cli_runner.invoke(dedupe_data, ['--fmt', 'CSV', 'specific.csv', 'output.csv'])
    assert result.exit_code == 0, f"CLI command failed: {result.output}"

    # Check that output.csv file exists and contains expected data
    assert os.path.exists('output.csv'), "Output file not created"

    deduped_df = pd.read_csv('output.csv')
    assert deduped_df.shape[0] == 12, "Expected 12 deduplicated records"
    assert deduped_df['cluster_id'].nunique() == 2, "Expected 2 unique clusters"

    # Clean up: delete output file
    os.remove('output.csv')
    os.remove('specific.csv')


def test_dedupe_data_with_json_output(cli_runner):
    """
    Test dedupe_data function with JSON output format.
    """

    # Prepare test data paths
    bad_data_path = 'deduplifhirLib/tests/test_data.csv'
    output_path = 'output.json'

    # Simulate CLI command execution
    result = cli_runner.invoke(dedupe_data, ['--fmt', 'CSV', bad_data_path, output_path])

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert os.path.exists(output_path), "Output file not created"

    # Check content of the output file (assuming it's JSON)
    deduped_df = pd.read_json(output_path)
    assert 'cluster_id' in deduped_df.columns, "Expected column 'cluster_id' not found"

    # Clean up: delete output file
    os.remove(output_path)

def test_dedupe_data_with_invalid_format(cli_runner):
    """
    Test dedupe_data function with an invalid data format.
    """

    # Prepare invalid test data paths
    bad_data_path = 'deduplifhirLib/tests/test_data_invalid.txt'
    output_path = 'output.csv'

    # Write some invalid content to the test file
    with open(bad_data_path, 'w',encoding='utf-8') as f:
        f.write("This is not a valid CSV or JSON file content")

    # Simulate CLI command execution
    result = cli_runner.invoke(dedupe_data, ['--fmt', 'CSV', bad_data_path, output_path])

    assert result.exit_code != 0, "CLI command should fail with invalid input format"
    assert not os.path.exists(output_path), "Output file should not be created"

    # Clean up: delete invalid test file if created
    if os.path.exists(output_path):
        os.remove(output_path)
    os.remove(bad_data_path)

def test_dedupe_accuracy(cli_runner):
    """
    Test dedupe_data function for deduplication accuracy using a dataset with known duplicates.
    """
    # Prepare test data
    test_data_csv = """id,truth_value,family_name,given_name,gender,birth_date,phone,street_address,city,state,postal_code,SSN
    1,duplicate,Smith,John,M,01/01/1990,,123 Elm St,Springfield,IL,62701,123-45-6789
    2,duplicate,Smyth,John,M,01/01/1990,,123 Elm St.,Springfield,IL,62701,123-45-6789
    3,unique,Doe,Jane,F,02/02/1992,,456 Oak St,Springfield,IL,62702,987-65-4321
    """
    with open('accuracy.csv', 'w',encoding='utf-8') as f:
        f.write(test_data_csv)

    # Simulate CLI command execution
    result = cli_runner.invoke(dedupe_data, ['--fmt', 'CSV', 'accuracy.csv', 'output_accuracy.csv'])

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert os.path.exists('output_accuracy.csv'), "Output file not created"

    # Check the deduplicated output
    deduped_df = pd.read_csv('output_accuracy.csv')
    assert deduped_df['cluster_id'].nunique() == 2, "Expected 2 unique clusters"

    # Clean up: delete output files
    os.remove('output_accuracy.csv')
    os.remove('accuracy.csv')

@pytest.mark.parametrize('generate_mock_data_fixture', [
    1000,
    5000,
    2500
],indirect=True)
def test_dedupe_data_with_large_dataset(generate_mock_data_fixture, cli_runner):
    """
    Test dedupe_data function with a large dataset.
    """
    # Generate a large dataset with the given rows and duplicate rate
    test_data_path = generate_mock_data_fixture
    output_path = 'large_output.csv'

    # Simulate CLI command execution
    result = cli_runner.invoke(dedupe_data, ['--fmt', 'CSV', test_data_path, output_path])

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert os.path.exists(output_path), "Output file not created"

    # Check that the output file is not empty
    deduped_df = pd.read_csv(output_path)
    assert len(deduped_df) > 0, "Output file should contain deduplicated records"

    # Clean up: delete output file
    os.remove(output_path)
    #os.remove(test_data_path)
