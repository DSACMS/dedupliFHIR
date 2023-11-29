#Copyright (c) 2021 Thomas Wyrick
# Taken from https://github.com/thomaswyrick/duplicate-data-generator

#This is a modified wrapper script to generate data using the Faker library
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


def generate_dup_data(column_file,output_name,rows,duprate,localization='en_US',cpus=1,batchsize=10000):
    config = {
        'column_file_path': column_file,
        'output_file': output_name,
        'total_row_cnt': rows,
        'duplication_rate': duprate,
        'localization': localization,
        'cpus': cpus,
        'batch_size': batchsize
    }
    #vars(parser.parse_args())

    with open(config['column_file_path']) as column_file:
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
    print('Elapsed time (sec) : {}'.format(end-start))
    print('Fin!')

def fix_aggregated_files(config):
    column_headers = ['truth_value']
    for column in config['columns']:
        column_headers.append(column['name'])

    main_file = pd.read_csv(config['output_file'], names=column_headers)
    main_file.drop(main_file.columns[0], axis=1)
    main_file.index = range(len(main_file.index))
    main_file.index.name = 'id'
    main_file.to_csv(config['output_file'])

def generate_temp_files(config, fake_gen):
    pool = Pool(config['cpus'])

    tmp_dir = './temp' 
    create_temp_directory(tmp_dir)

    batch_size = config['batch_size']
    num_batches = ceil(config['total_row_cnt']/batch_size)
    remaining_rows = config['total_row_cnt']

    for _ in range(num_batches):
        pool.apply_async(create_fake_data_file, args = (config, fake_gen, tmp_dir, batch_size, remaining_rows))
    pool.close()
    pool.join()
    return tmp_dir


def combine_temp_files(tmp_dir, output_file):
    if os.path.isfile(output_file):
        os.remove(output_file)
    with open(output_file, 'wb') as outfile:
        for filename in glob.glob(tmp_dir + '/*'):
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)


def create_fake_data_file(config, fake_gen, tmp_dir, batch_size, remaining_rows):
    if remaining_rows > batch_size:
        rows_to_process = batch_size
    else:
        rows_to_process = remaining_rows
    remaining_rows = remaining_rows - rows_to_process
    
    num_of_initial_rows, num_duplicated_rows = get_row_counts(rows_to_process, config['duplication_rate'])
    try:
        fake_data = get_fake_data(num_of_initial_rows, num_duplicated_rows, config['columns'], fake_gen)
        temp_file_name = tmp_dir + '/' + str(uuid.uuid4())
        print('Writing {} rows to file'.format(rows_to_process))
        fake_data.to_csv(temp_file_name, header=False)
    except Exception as e:
        print('Unexpected error: {}'.format(e))
        raise e


def create_temp_directory(tmp_dir):
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

def get_fake_data(num_of_initial_rows, num_duplicated_rows, columns, fake_gen):
    initial_fake_data = pd.DataFrame()

    for column in columns:
        fill_rate = 100
        if 'fill_rate' in column:
            fill_rate = column['fill_rate'] * 100
        initial_fake_data[column['name']] = [get_fake_string(column['type'], fake_gen, fill_rate) for x in range(num_of_initial_rows)]

    initial_fake_data.insert(0, 'truth_value', '')
    initial_fake_data['truth_value'] = [uuid.uuid4() for _ in range(len(initial_fake_data.index))]

    known_duplicates = initial_fake_data.sample(num_duplicated_rows, replace=True)

    for column in columns:
        if 'transposition_chars' in column and column['transposition_chars'] > 0:
            for _ in range(column['transposition_chars']):
                known_duplicates[column['name']] = known_duplicates[column['name']].apply(transposition_chars)
        if 'mistype_chars' in column and column['mistype_chars'] > 0:
            for i in range(column['mistype_chars']):
                known_duplicates[column['name']] = known_duplicates[column['name']].apply(transposition_chars)

    output_data = pd.concat([initial_fake_data, known_duplicates])
    return output_data


def get_row_counts(total_row_cnt, duplication_rate):
    num_of_initial_rows = int(total_row_cnt - int(total_row_cnt * duplication_rate))
    num_duplicated_rows = int(total_row_cnt - num_of_initial_rows)
    return num_of_initial_rows,num_duplicated_rows


def get_fake_string(fake_type, fake_gen, fill_rate):
    if random.randrange(100) > fill_rate:
        return ''
    gender = np.random.choice(["M", "F"], p=[0.5, 0.5])

    if fake_type == 'first_name':
        return fake_gen.first_name_male() if gender=="M" else fake_gen.first_name_female()
        #return fake_gen.first_name()
    elif fake_type == 'last_name':
        return fake_gen.last_name()
    elif fake_type == 'street_address':
        return fake_gen.street_address()
    elif fake_type == 'secondary_address':
        return fake_gen.secondary_address()
    elif fake_type == 'city':
        return fake_gen.city()
    elif fake_type == 'state':
        return fake_gen.state()
    elif fake_type == 'postcode':
        return fake_gen.postcode()
    elif fake_type == 'current_country':
        return fake_gen.current_country()
    elif fake_type == 'phone_number':
        t = fake_gen.phone_number()
        if 'x' in t:
            t = None
        return t
    elif fake_type == 'email':
        return fake_gen.email()
    elif fake_type == 'ssn':
        return fake_gen.ssn()
    elif fake_type == 'gender':
        return gender
    elif fake_type == 'date_of_birth':
        return fake_gen.date_of_birth(minimum_age=18, maximum_age=95).strftime('%m/%d/%Y')

def transposition_chars(str_to_alter):
    if  str_to_alter == None or len(str_to_alter) < 1:
        return str_to_alter
    first_char = random.randrange(len(str_to_alter)-1)
    second_char = first_char + 1
    split_str = split(str_to_alter)
    tmp = split_str[first_char]
    split_str[first_char] = split_str[second_char]
    split_str[second_char] = tmp
    str_to_alter = combine(split_str)
    return str_to_alter

def mistype_chars(str_to_alter):
    if len(str_to_alter) < 1 or str_to_alter == None:
        return str_to_alter

    char_to_alter = random.randrange(len(str_to_alter))
    split_str = split(str_to_alter)
    split_str[char_to_alter] = random.choice(string.ascii_letters)
    str_to_alter = combine(split_str)
    return str_to_alter

def split(word):
    return [char for char in word]

def combine(chars):
    new_str = ''
    for char in chars:
        new_str += char
    return new_str