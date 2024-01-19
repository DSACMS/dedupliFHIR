"""
Module to define cli for ecqm-deduplifhir library.
"""
import click
from splink.duckdb.blocking_rule_library import block_on
from deduplifhirLib.utils import use_linker

#Register cli as a group of commands invoked in the format ecqm_dededuplifhir <bad_data> <output>
@click.group()
def cli():
    """ Defines the click cli object """

#seemlingly unused arguments are likely used by the use_linker cm -IM
@click.command()
@click.option('--fmt', default="FHIR", help='Format of patient data')
@click.argument('bad_data_path')
@click.argument('output_path')
@use_linker
def dedupe_data(fmt,bad_data_path, output_path,linker=None): #pylint: disable=unused-argument
    """Program to dedupe patient data in many formats namely FHIR and QRDA"""

    #linker is created by use_linker decorator
    blocking_rule_for_training = block_on(["given_name", "family_name"])
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    blocking_rule_for_training = block_on("substr(birth_date, 1, 4)")  # block on year
    linker.estimate_parameters_using_expectation_maximisation(
        blocking_rule_for_training, estimate_without_term_frequencies=True)

    pairwise_predictions = linker.predict()

    clusters = linker.cluster_pairwise_predictions_at_threshold(pairwise_predictions, 0.95)

    deduped_record_mapping = clusters.as_pandas_dataframe()

    if fmt != "TEST":
        deduped_record_mapping = deduped_record_mapping.drop(deduped_record_mapping[deduped_record_mapping.path == "TRAINING"].index)

    path_to_write = output_path + "deduped_record_mapping.xlsx"
    deduped_record_mapping.to_excel(path_to_write)


cli.add_command(dedupe_data)

if __name__ == "__main__":
    cli()
