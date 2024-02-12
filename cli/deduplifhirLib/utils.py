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
from splink.duckdb.linker import DuckDBLinker

from deduplifhirLib.settings import SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE, read_fhir_data


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
                "ssn": [row[11]],
                "path": ["TRAINING" if marked else ""]
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
        fmt = kwargs['fmt']
        data_dir = kwargs['bad_data_path']

        print(f"Format is {fmt}")
        print(f"Data dir is {data_dir}")

        training_df = parse_test_data('cli/deduplifhirLib/test_data.csv',marked=True)
        if fmt == "FHIR":
            train_frame = pd.concat([parse_fhir_data(data_dir),training_df])
        elif fmt == "QRDA":
            train_frame = pd.concat([parse_qrda_data(data_dir),training_df])
        elif fmt == "CSV":
            train_frame = pd.concat([parse_test_data(data_dir),training_df])
        elif fmt == "TEST":
            train_frame = training_df


        lnkr = DuckDBLinker(train_frame, SPLINK_LINKER_SETTINGS_PATIENT_DEDUPE)
        lnkr.estimate_u_using_random_sampling(max_pairs=5e6)

        kwargs['linker'] = lnkr
        return func(*args,**kwargs)

    return wrapper
