import os
from os import walk
import json
import pandas as pd
from splink.duckdb.linker import DuckDBLinker
import splink.duckdb.comparison_library as cl
import splink.duckdb.comparison_template_library as ctl
from splink.duckdb.blocking_rule_library import block_on
from splink.datasets import splink_datasets

from contextlib import contextmanager
from deduplifhirLib.settings import settings, DEDUPE_VARS

from . import base_dir

#Fhir stores patient data in directories of json
def parse_fhir_data(path):
    #Get all files in path with fhir data.
    all_patient_records = [
        os.path.join(dirpath,f) for (dirpath, dirnames, filenames)
         in os.walk(path) for f in filenames]
    
    list_of_patient_record_dicts = []

    for patient_record in all_patient_records:
        with open(patient_record, "r") as f:
            patient_json_record = json.load(f)
        
        patient_dict = {
            "family_name": patient_json_record['entry'][0]['resource']['name'][0]['family'],
            "given_name": patient_json_record['entry'][0]['resource']['name'][0]['given'][0],
            "gender": patient_json_record['entry'][0]['resource']['gender'],
            "birth_date": patient_json_record['entry'][0]['resource']['birthDate'],
            "phone": patient_json_record['entry'][0]['resource']['telecom'][0]['value'],
            "street_address": patient_json_record['entry'][0]['resource']['address'][0]['line'][0],
            "city": patient_json_record['entry'][0]['resource']['address'][0]['city'],
            "state": patient_json_record['entry'][0]['resource']['address'][0]['state'],
            "postal_code": patient_json_record['entry'][0]['resource']['address'][0]['postalCode']
        }
        list_of_patient_record_dicts.append(patient_dict)
    
    if len(list_of_patient_record_dicts) == 0:
        return pd.DataFrame(list_of_patient_record_dicts)
    else:
        return []


@contextmanager
def use_linker(*args, **kwargs):

    slug = args[0]

    data_dir = os.path.join(base_dir, "_data", slug)

    df = parse_fhir_data(data_dir)

    linker = DuckDBLinker(df, settings)
    linker.estimate_u_using_random_sampling(max_pairs=5e6)

    yield linker
