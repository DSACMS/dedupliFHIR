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
@click.option('--html', is_flag=True)
@click.argument('output_path', default=CACHE_DIR)
@click.argument('processed_patient_data_path', default=CACHE_DIR)
def gen_diff(html,output_path,processed_patient_data_path):
    """
    dedupliFHIR cli command to generate diffs between duplicate patients and save them

    Arguments:
        fmt: Format of output data from dedupe-data
        processed_patient_data_path: path of output data, when left as default uses cache
        output_path: Optional path of processed data output file mapping
    """

    #Get text from csv with dupes
    cache_df = pd.read_csv(processed_patient_data_path + "dedupe-cache.csv")

    #Get a dataframe with all of the paths concatenated attached to their cluster id.
    grouped_dirs = cache_df.groupby('cluster_id')['path'].apply(' '.join).reset_index()

    #convert to list
    pat_list = grouped_dirs.to_dict('records')
    for unique_patient_record in pat_list:
        list_of_files = unique_patient_record['path'].split()

        if (num_files := len(list_of_files)) > 1:
            print(list_of_files)

        if num_files == 2:
            #generate diff if we can.
            if not html:
                diff_gen = gen_regular_diff(list_of_files[0], list_of_files[1])
            else:
                diff_gen = gen_html_diff(list_of_files[0], list_of_files[1])

            if not diff_gen:
                return

            #save diff to file.
            dfname = output_path + str(unique_patient_record['cluster_id']) + ".diff"
            with open(dfname ,"w",encoding="utf-8") as f:
                for line in diff_gen:
                    f.write(str(line))



def gen_regular_diff(path_one, path_two):
    try:
        with open(path_one,'r',encoding="utf-8") as right_file:
            with open(path_two,'r',encoding="utf-8") as right_file:
                diff = difflib.unified_diff(
                    right_file.readlines(),
                    right_file.readlines())

                return diff
    except FileNotFoundError:
        return []

def gen_html_diff(path_one, path_two):
    try:
        with open(path_one,'r',encoding="utf-8") as right_file:
            with open(path_two,'r',encoding="utf-8") as right_file:
                diff = difflib.HtmlDiff().make_file(
                    right_file.readlines(),
                    right_file.readlines()
                )

                return diff
    except FileNotFoundError:
        return []


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
cli.add_command(gen_diff)
cli.add_command(clear_cache)
cli.add_command(status)

if __name__ == "__main__":
    cli()
