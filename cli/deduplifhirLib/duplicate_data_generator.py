"""
Copyright (c) 2021 Thomas Wyrick
Taken from https://github.com/thomaswyrick/duplicate-data-generator

This is a modified wrapper script to generate data using the Faker library
"""
import json
import os
import glob
import time
import shutil
import random
import uuid
import string
from multiprocessing import Pool
from math import ceil
import pandas as pd
import numpy as np
from faker import Faker


def generate_dup_data(column_file,output_name,rows,duprate,localization='en_US',batchsize=10000):
    """
    This function generates mock patient data and saves it to a CSV

    Arguments:
        column_file: The path defining the datatypes desired for each patient
        output_name: The path defining the output CSV
        rows: Amount of fake patients to generate
        duprate: Ratio of duplicates
        localization: Text locale
        batchsize: amount to generate at once
    """

    config = {
        'column_file_path': column_file,
        'output_file': output_name,
        'total_row_cnt': rows,
        'duplication_rate': duprate,
        'localization': localization,
        'cpus': 1,
        'batch_size': batchsize
    }
    #vars(parser.parse_args())

    with open(config['column_file_path'],encoding="utf-8") as column_file:
        col_config = json.load(column_file)

    config.update(col_config) # append column settings to main config dict

    start = time.time()
    fake_gen = Faker(config['localization'])
    tmp_dir = generate_temp_files(config, fake_gen)
    output_file = config['output_file']
    combine_temp_files(tmp_dir, output_file)
    fix_aggregated_files(config)
    shutil.rmtree(tmp_dir)
    end = time.time()
    print(f"Elapsed time (sec) : {end-start}")
    print('Fin!')

def fix_aggregated_files(config):
    """
    Unifies indices between agregated CSV files after the merge

    Arguments:
        config: Config dict
    """
    column_headers = ['truth_value']
    for column in config['columns']:
        column_headers.append(column['name'])

    main_file = pd.read_csv(config['output_file'], names=column_headers)
    main_file.drop(main_file.columns[0], axis=1)
    main_file.index = range(len(main_file.index))
    main_file.index.name = 'id'
    main_file.to_csv(config['output_file'])

def generate_temp_files(config, fake_gen):
    """
    Generates each batch inside a specific temp file asychronously

    Arguments:
        config: config dict
        fake_gen: Faker generation object
    """

    pool = Pool(config['cpus'])

    tmp_dir = './temp'
    create_temp_directory(tmp_dir)

    batch_size = config['batch_size']
    num_batches = ceil(config['total_row_cnt']/batch_size)
    remaining_rows = config['total_row_cnt']

    for _ in range(num_batches):
        pool.apply_async(
            create_fake_data_file, args = (config, fake_gen, tmp_dir, batch_size, remaining_rows))
    pool.close()
    pool.join()
    return tmp_dir


def combine_temp_files(tmp_dir, output_file):
    """
    Combines each temp file that is the result of each async batch.

    Arguments:
        tmp_dir: path to temp files
        output_file: path to save the results to
    """

    if os.path.isfile(output_file):
        os.remove(output_file)
    with open(output_file, 'wb') as outfile:
        for filename in glob.glob(tmp_dir + '/*'):
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)


def create_fake_data_file(config, fake_gen, tmp_dir, batch_size, remaining_rows):
    """
    Creates fake data tmp files based on the batch size of each file

    Arguments:
        config: config dict
        fake_gen: Faker generation object
        tmp_dir: path to temp directory
        batch_size: size of each temp file
        remaining_rows: total amount of records to generate
    """

    if remaining_rows > batch_size:
        rows_to_process = batch_size
    else:
        rows_to_process = remaining_rows
    remaining_rows = remaining_rows - rows_to_process

    num_of_initial_rows, num_duplicated_rows = get_row_counts(
        rows_to_process, config['duplication_rate'])
    try:
        fake_data = get_fake_data(
            num_of_initial_rows, num_duplicated_rows, config['columns'], fake_gen)
        temp_file_name = tmp_dir + '/' + str(uuid.uuid4())
        print(f"Writing {rows_to_process} rows to file")
        fake_data.to_csv(temp_file_name, header=False)
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise e


def create_temp_directory(tmp_dir):
    """
    Creates a temporary directory

    Arguments:
        tmp_dir: path to temp files
    """

    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

def get_fake_data(num_of_initial_rows, num_duplicated_rows, columns, fake_gen):
    """
    Creates fake data and stores it in a pandas dataframe

    Arguments:
        num_of_initial_rows: number of non duplicate rows
        num_duplicated_rows: number of duplicate rows
        columns: columns for patient data
        fake_gen: Faker generation object
    """

    initial_fake_data = pd.DataFrame()

    for column in columns:
        fill_rate = 100
        if 'fill_rate' in column:
            fill_rate = column['fill_rate'] * 100

        fake_strings = [
            get_fake_string(column['type'], fake_gen, fill_rate) for x in range(num_of_initial_rows)
        ]
        initial_fake_data[column['name']] = fake_strings

    initial_fake_data.insert(0, 'truth_value', '')
    initial_fake_data['truth_value'] = [uuid.uuid4() for _ in range(len(initial_fake_data.index))]

    known_duplicates = initial_fake_data.sample(num_duplicated_rows, replace=True)

    for column in columns:
        if 'transposition_chars' in column and column['transposition_chars'] > 0:
            for _ in range(column['transposition_chars']):
                known_duplicates[column['name']] = known_duplicates[column['name']].apply(
                    transposition_chars)
        if 'mistype_chars' in column and column['mistype_chars'] > 0:
            for _ in range(column['mistype_chars']):
                known_duplicates[column['name']] = known_duplicates[column['name']].apply(
                    transposition_chars)

    output_data = pd.concat([initial_fake_data, known_duplicates])
    return output_data


def get_row_counts(total_row_cnt, duplication_rate):
    """
    Gets the number of duplicates and non-duplicate data rows
    as a tuple.

    Arguments:
        total_row_cnt: total rows of fake data requested
        duplication_rate: rate of dup generation.
    
    Returns:
        A tuple with the number of initial rows followed by
        the number of duplicates.
    """

    num_of_initial_rows = int(total_row_cnt - int(total_row_cnt * duplication_rate))
    num_duplicated_rows = int(total_row_cnt - num_of_initial_rows)
    return num_of_initial_rows,num_duplicated_rows


def get_fake_string(fake_type, fake_gen, fill_rate):
    """
    Generates and returns a part of a record generated by Faker

    Arguments:
        fake_type: Type of fake personal data desired
        fake_gen: The Faker generation object
        fill_rate: Rate of records to leave blank or not
    
    Returns:
        String of Faker data
    """

    if random.randrange(100) > fill_rate:
        return ''
    gender = np.random.choice(["M", "F"], p=[0.5, 0.5])

    if fake_type == 'first_name':
        return fake_gen.first_name_male() if gender=="M" else fake_gen.first_name_female()
        #return fake_gen.first_name()
    if fake_type == 'last_name':
        return fake_gen.last_name()
    if fake_type == 'street_address':
        return fake_gen.street_address()
    if fake_type == 'secondary_address':
        return fake_gen.secondary_address()
    if fake_type == 'city':
        return fake_gen.city()
    if fake_type == 'state':
        return fake_gen.state()
    if fake_type == 'postcode':
        return fake_gen.postcode()
    if fake_type == 'current_country':
        return fake_gen.current_country()
    if fake_type == 'phone_number':
        t = fake_gen.phone_number()
        if 'x' in t:
            t = None
        return t
    if fake_type == 'email':
        return fake_gen.email()
    if fake_type == 'ssn':
        return fake_gen.ssn()
    if fake_type == 'gender':
        return gender
    if fake_type == 'date_of_birth':
        return fake_gen.date_of_birth(minimum_age=18, maximum_age=95).strftime('%m/%d/%Y')

def transposition_chars(str_to_alter):
    """
    Alters and adds errors to a string

    Arguments:
        str_to_alter: String to cause mistakes in
    
    Returns:
        Altered input string
    """

    if  str_to_alter is None or len(str_to_alter) < 1:
        return str_to_alter
    first_char = random.randrange(len(str_to_alter)-1)
    second_char = first_char + 1
    split_str = [*str_to_alter]
    tmp = split_str[first_char]
    split_str[first_char] = split_str[second_char]
    split_str[second_char] = tmp
    str_to_alter = ''.join(split_str)
    return str_to_alter

def mistype_chars(str_to_alter):
    """
    Alters and adds mistypes to a string

    Arguments:
        str_to_alter: String to cause mistakes in
    
    Returns:
        Altered input string
    """
    if len(str_to_alter) < 1 or str_to_alter is None:
        return str_to_alter

    char_to_alter = random.randrange(len(str_to_alter))
    split_str = [*str_to_alter]
    split_str[char_to_alter] = random.choice(string.ascii_letters)
    str_to_alter = ''.join(split_str)
    return str_to_alter
