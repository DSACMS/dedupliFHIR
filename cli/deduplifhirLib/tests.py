"""
This module defines pytest testing functions and fixtures for testing the deduplication functionality using Splink.
"""

import os
from pathlib import Path
from io import StringIO
import pytest
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch
from splink.duckdb.linker import DuckDBLinker
from splink.duckdb.blocking_rule_library import block_on
from deduplifhirLib.duplicate_data_generator import generate_dup_data
from deduplifhirLib.settings import SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE
from deduplifhirLib.utils import parse_test_data, use_linker
from cli.ecqm_dedupe import dedupe_data


@pytest.fixture
def mock_use_linker():
    """
    Fixture to mock the use_linker decorator and return a mock linker object.
    """
    with patch('deduplifhirLib.utils') as mock_use_linker:
        mock_linker = mock_use_linker.return_value.__enter__.return_value
        yield mock_linker

@pytest.fixture
def cli_runner():
    """
    Fixture to provide a CliRunner instance to invoke Click commands programmatically.
    """
    return CliRunner()

def test_dedupe_data_with_csv_output(mock_use_linker, cli_runner):
    """
    Test dedupe_data function with CSV output format.
    """
    # Mock linker behavior
    mock_use_linker.side_effect = lambda func: func(linker=mock_use_linker)

    # Prepare test data paths
    bad_data_path = 'deduplifhirLib/test_data.csv'
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

def test_dedupe_data_with_specific_csv(mock_use_linker, cli_runner):
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
    with open('specific.csv', 'w') as f:
        f.write(test_data_csv)

    # Mock linker behavior
    mock_use_linker.side_effect = lambda func: func(linker=mock_use_linker)

    # Simulate CLI command execution
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
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