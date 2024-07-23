"""
Module to define cli for ecqm-deduplifhir library.
"""
import os
import os.path
import difflib
import pandas as pd
import click
from splink.duckdb.blocking_rule_library import block_on
from deduplifhirLib.utils import use_linker


CACHE_DIR = "/tmp/"

#Register cli as a group of commands invoked in the format ecqm_dededuplifhir <bad_data> <output>
@click.group()
def cli():
    """ Set of CLI commands to appy Splink data linkage and deduplication for FHIR data """

#seemlingly unused arguments are likely used by the use_linker cm -IM
@click.command()
@click.option('--fmt', default="FHIR", help='Format of patient data')
@click.argument('bad_data_path')
@click.argument('output_path')
@use_linker
def dedupe_data(fmt,bad_data_path, output_path,linker=None): #pylint: disable=unused-argument
    """Program to dedupe patient data in many formats namely FHIR and QRDA"""

    print(os.getcwd())
    #linker is created by use_linker decorator
    blocking_rule_for_training = block_on("ssn")
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training)

    blocking_rule_for_training = block_on("birth_date")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training)

    blocking_rule_for_training = block_on(["street_address", "postal_code"])
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training)


    pairwise_predictions = linker.predict()

    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)

    deduped_record_mapping = clusters.as_pandas_dataframe()

    if fmt != "TEST":
        deduped_record_mapping = deduped_record_mapping.drop(
            deduped_record_mapping[deduped_record_mapping.path == "TRAINING"].index)

    #Calculate only uniques
    unique_records = deduped_record_mapping.drop_duplicates(subset=['cluster_id'])
    #cache results
    #TODO: make platform agnostic
    deduped_record_mapping.to_csv(CACHE_DIR + "dedupe-cache.csv")
    unique_records.to_csv(CACHE_DIR + "unique-records-cache.csv")


    _, extension = os.path.splitext(output_path)

    if extension == '.xlsx':
        deduped_record_mapping.to_excel(output_path)
    elif extension == '.csv':
        deduped_record_mapping.to_csv(output_path)
    elif extension == '.json':
        deduped_record_mapping.to_json(output_path)
    elif extension == '.html':
        deduped_record_mapping.to_html(output_path)
    elif extension == '.xml':
        deduped_record_mapping.to_xml(output_path)
    elif extension == '.tex':
        deduped_record_mapping.to_latex(output_path)
    elif extension == '.feather':
        deduped_record_mapping.to_feather(output_path)
    else:
        raise ValueError("File format not supported!")
    #path_to_write = output_path + "deduped_record_mapping.xlsx"
    #deduped_record_mapping.to_excel(path_to_write)


@click.command()
def clear_cache():
    """Clear cache of dedupliFHIED patient data"""
    os.remove(CACHE_DIR + "unique-records-cache.csv")
    os.remove(CACHE_DIR + "dedupe-cache.csv")
    print("Cache cleared.")

@click.command()
def status():
    """Output status of cache as well as result and stats of last run"""

    try:
        #Print amount of duplicates found in cache if found
        cache_df = pd.read_csv(CACHE_DIR + "dedupe-cache.csv")
    except FileNotFoundError:
        print("Cache is empty")
        return

    print("Cache contains data")
    number_patients = cache_df.cluster_id.nunique(dropna=True)

    number_total = cache_df.unique_id.nunique(dropna=True)

    print(f"There were {number_total - number_patients} duplicates found last run.")

    print(
        f"There are {number_patients} unique patients among " +
        f"{number_total} records among the data.")


cli.add_command(dedupe_data)
cli.add_command(clear_cache)
cli.add_command(status)

if __name__ == "__main__":
    cli()
