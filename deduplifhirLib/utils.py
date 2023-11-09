import os
from os import walk
import json
import pandas as pd
from multiprocessing import Pool
from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from splink.datasets import splink_datasets

from contextlib import contextmanager
from settings import settings, DEDUPE_VARS, read_fhir_data

from __init__ import base_dir



#Fhir stores patient data in directories of json
def parse_fhir_data(path, cpu_cores=4):
    #Get all files in path with fhir data.
    all_patient_records = [
        os.path.join(dirpath,f) for (dirpath, dirnames, filenames)
         in os.walk(path) for f in filenames if f.split(".")[-1] == "json"]
    
    print(len(all_patient_records))
    list_of_patient_record_dicts = []

    #Load files concurrently via multiprocessing
    print(f"Reading files with {cpu_cores} cores...")
    pool = Pool(cpu_cores)
    df_list = pool.map(read_fhir_data, all_patient_records)

    print("Done parsing fhir data.")
    return pd.concat(df_list)

@contextmanager
def use_linker(*args, **kwargs):

    slug = args[0]

    data_dir = os.path.join(base_dir, "_data", slug)

    df = parse_fhir_data(data_dir)

    linker = DuckDBLinker(df, settings)
    linker.estimate_u_using_random_sampling(max_pairs=5e6)

    yield linker

if __name__ == "__main__":
    linker = DuckDBLinker(parse_fhir_data('/Users/murt/Downloads/synthea_1m_fhir_1_8/output_1/fhir'), settings)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)
    
    blocking_rule_for_training = block_on(["given_name", "family_name"])
    
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    blocking_rule_for_training = block_on("birth_date(dob, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    
    pairwise_predictions = linker.predict()
    
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)
    
    print(clusters.as_pandas_dataframe(limit=25))