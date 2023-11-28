import os
import time
from os import walk
import json
import sys
from pathlib import Path
import csv
import datetime
import pandas as pd
from multiprocessing import Pool
from functools import wraps
from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from splink.datasets import splink_datasets
import uuid
from contextlib import contextmanager
from settings import SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE, read_fhir_data
from duplicate_data_generator import generate_dup_data


base_dir = os.path.abspath(os.path.dirname(__file__))


def parse_qrda_data(path,cpu_cores=4):
    raise NotImplementedError


#Fhir stores patient data in directories of json
def parse_fhir_data(path, cpu_cores=4,parse_function=read_fhir_data):
    """
    This function parses all json files in a given path structure as FHIR data. It walks
    through the given path and parses each json file it finds into a pandas Dataframe.

    The process of parsing the files is done through a number of processes that each read the
    JSON and output the Dataframe in parallel. The master process then returns the result of 
    concatenating each dataframe into a full record of FHIR data.

    Arguments:
        path: Directory path to walk through to look for JSON FHIR data
        cpu_cores: Number of processes to use at once to parse the JSON FHIR data
    
    Returns:
        Dataframe containing all patient FHIR data
    """
    #Get all files in path with fhir data.
    all_patient_records = [
        os.path.join(dirpath,f) for (dirpath, dirnames, filenames)
         in os.walk(path) for f in filenames if f.split(".")[-1] == "json"]
    
    print(len(all_patient_records))

    #Load files concurrently via multiprocessing
    print(f"Reading files with {cpu_cores} cores...")
    start = time.time()
    pool = Pool(cpu_cores)
    df_list = pool.map(parse_function, all_patient_records)

    print(f"Read fhir data in {time.time() - start} seconds")
    print("Done parsing fhir data.")
    return pd.concat(df_list)

def parse_test_data(path):

    df_list = []
    # reading csv file
    with open(path, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)

        fields = next(csvreader)


        for row in csvreader:
            #print(row[2])
            dob = datetime.datetime.strptime(row[5], '%m/%d/%Y').strftime('%Y-%m-%d')
            patient_dict = {
                "unique_id": uuid.uuid4().int,
                "family_name": [row[2]],
                "given_name": [row[3]],
                "gender": [row[4]],
                "birth_date": [dob],
                "phone": [row[6]],
                "street_address": [row[7]],
                "city": [row[8]],
                "state": [row[9]],
                "postal_code": [row[10]],
                "ssn": [row[11]]
            }

            df_list.append(pd.DataFrame(patient_dict))
    
    return pd.concat(df_list)
    


def use_linker(func):
    """
    A contextmanager that is used to obtain a linker object with which to dedupe patient 
    records with. Automatically reads in the FHIR data for the requested dataset marked 
    by a slug.

    Arguments:
        slug: ID for the dataset to dedupe
    
    Returns:
        linker: the linker object to use for deduplication. 
    """

    @wraps(func)
    def wrapper(*args,**kwargs):
        format = kwargs['format']
        data_dir = kwargs['bad_data_path']

        print(f"Format is {format}")
        print(f"Data dir is {data_dir}")

        if format == "FHIR":
            df = parse_fhir_data(data_dir)
        elif format == "QRDA":
            df = parse_qrda_data(data_dir)
        
        linker = DuckDBLinker(df, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
        linker.estimate_u_using_random_sampling(max_pairs=5e6)

        kwargs['linker'] = linker
        return func(*args,**kwargs)
    
    return wrapper

if __name__ == "__main__":

    testPath = (Path(__file__).parent).resolve()
    print(testPath)

    csvPath = str(testPath) + "/test_data.csv"
    column_path = str(testPath) + "/test_data_columns.json"

    #Create test data
    generate_dup_data(column_path, csvPath, 10000, 0.20)

    df = parse_test_data(csvPath)

    linker = DuckDBLinker(df, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
    linker.estimate_u_using_random_sampling(max_pairs=1e6)
    
    blocking_rule_for_training = block_on(["given_name", "family_name"])
    
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    blocking_rule_for_training = block_on("substr(birth_date, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(blocking_rule_for_training, estimate_without_term_frequencies=True)
    
    
    pairwise_predictions = linker.predict()
    
    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)
    
    print(clusters.as_pandas_dataframe(limit=25))
