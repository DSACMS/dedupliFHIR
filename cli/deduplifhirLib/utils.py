"""
Below are the definition of the utils used by the dedupliFHR tool.

The most important of these data structures is the context manager for linker 
generation for Splink. 

"""
import os
import time
import csv
import datetime
import uuid
from multiprocessing import Pool
from functools import wraps
import pandas as pd
#from splink.duckdb.linker import DuckDBLinker
from splink import DuckDBAPI, Linker

from deduplifhirLib.settings import (
    SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE, BLOCKING_RULE_STRINGS, read_fhir_data
)
from deduplifhirLib.normalization import (
    normalize_addr_text, normalize_name_text, normalize_date_text
)

base_dir = os.path.abspath(os.path.dirname(__file__))


def check_blocking_uniques(check_df,blocking_field,required_uniques=5):
    """
    Function that takes in a dataframe and asserts the required blocking values
    are present for splink to use. Throws an assertion error if it can't.

    Arguments:
        check_df: Pandas Dataframe to check
        blocking_field: Column of the frame to check uniques of
        required_uniques: Unique values to require for blocking rules
    """
    uniques = getattr(check_df, blocking_field).nunique(dropna=True)
    assert uniques >= required_uniques


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
    df_list = []
    start = time.time()
    with Pool(cpu_cores) as pool:
        df_list = pool.map(parse_function, all_patient_records)

    print(f"Read fhir data in {time.time() - start} seconds")
    print("Done parsing fhir data.")

    return pd.concat(df_list)

def parse_test_data(path,marked=False):
    """
    This function parses a csv file in a given path structure as patient data. It
    parses through the csv and creates a dataframe from it. 

    Arguments:
        path: Path of CSV file
    Returns:
        Dataframe containing all patient data
    """

    df_list = []
    # reading csv file
    with open(path, 'r',encoding="utf-8") as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)

        _ = next(csvreader)


        for row in csvreader:
            #print(row[2])
            try:
                #dob = datetime.datetime.strptime(row[5], '%m/%d/%Y').strftime('%Y-%m-%d')
                patient_dict = {
                    "unique_id": uuid.uuid4().int,
                    "family_name": [normalize_name_text(row[2])],
                    "given_name": [normalize_name_text(row[3])],
                    "gender": [row[4]],
                    "birth_date": [normalize_date_text(row[5])],
                    "phone": [row[6]],
                    "street_address": [normalize_addr_text(row[7])],
                    "city": [normalize_addr_text(row[8])],
                    "state": [normalize_addr_text(row[9])],
                    "postal_code": [row[10]],
                    "ssn": [row[11]],
                    "path": ["TRAINING" if marked else ""]
                }

                df_list.append(pd.DataFrame(patient_dict))
            except IndexError:
                print("could not read row")

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
        fmt = kwargs['fmt']
        data_dir = kwargs['bad_data_path']

        print(f"Format is {fmt}")
        print(f"Data dir is {data_dir}")
        print(os.getcwd())

        dir_path = os.path.dirname(os.path.realpath(__file__))

        training_df = parse_test_data(dir_path + '/tests/test_data.csv',marked=True)

        if fmt == "FHIR":
            train_frame = pd.concat([parse_fhir_data(data_dir),training_df])
        elif fmt == "QRDA":
            train_frame = pd.concat([parse_qrda_data(data_dir),training_df])
        elif fmt == "CSV":
            train_frame = pd.concat([parse_test_data(data_dir),training_df])
        elif fmt == "TEST":
            train_frame = training_df
        elif fmt == "DF":
            train_frame = data_dir
        else:
            raise ValueError('Unrecognized format to parse')

        #check blocking values
        for rule in BLOCKING_RULE_STRINGS:
            try:
                if isinstance(rule, list):
                    for sub_rule in rule:
                        check_blocking_uniques(train_frame, sub_rule)
                else:
                    check_blocking_uniques(train_frame, rule)
            except AssertionError as e:
                print(f"Could not assert the proper number of unique records for rule {rule}")
                raise e

        #lnkr = DuckDBLinker(train_frame, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
        lnkr = Linker(train_frame,SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE,db_api=DuckDBAPI())
        lnkr.training.estimate_u_using_random_sampling(max_pairs=5e6)

        kwargs['linker'] = lnkr
        return func(*args,**kwargs)

    return wrapper
