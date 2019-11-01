'''
This file provides helper functions to visualize or view data in a directory
This also contains some tools to aid in editting the data on the fly to change column types
while viewing files

TODO:
fix order of these functions
'''

import pandas as pd
import re
import os
from pathlib import Path
from collections import defaultdict
import numpy as np
from pprint import pprint
from glob import glob
import os.path
import pdb


def _is_csv(file_path):
    csv_ptn = '(?<=\.)csv$'
    return re.search(csv_ptn, file_path)

def _is_xl(file_path):
    excel_ptn = '(?<=\.)xl\w*$'
    return re.search(excel_ptn, file_path)

def _is_tabular(file_path):
    return _is_csv(file_path) or _is_xl(file_path)

def read_file_path(file_path, sheet=0):
    try:
        if _is_csv(file_path):
            return pd.read_csv(file_path)
        elif _is_xl(file_path):
            return pd.read_excel(file_path, sheet_name=sheet)
    except Exception as e:
        print('file not found! make sure you inputted the directory correctly')
        print('file path given: ', file_path)
        raise e

def _print_df_summary(file_path, sheet):
    file_path = file_path.lower()
    print('printing summary for ', file_path)
    df = read_file_path(file_path, sheet=sheet)
    print(df.dtypes)
    print('rows: {}, columns: {}'.format(len(df.index),len(df.columns)))

# gets the file paths of each tabular data file in the directory 
def _get_tabular_paths_in_dir(dir_):
    file_paths = [dir_ + file_name for file_name in os.listdir(dir_) if _is_tabular(file_name)]
    return file_paths
     
# print summary of dataframes in directory dir_ if no specific country is specified
def _print_dir_summary(dir_, sheet, country=None):
    if country:
        group = country
        file_paths = glob(dir_ + '*' + country + '*')
    else:
        group = 'all countries'
        file_paths = _get_tabular_paths_in_dir(dir_)
    print('printing dataframe summary for ' + group + '...')
    file_paths.sort()
    for path in file_paths:
        _print_df_summary(path, sheet)
        print('\n')
        
def _is_valid_type(type_):
    return (type_ == np.int64) or (type_ == np.float64)

# pretty print the dictionary, seperate from python pprint
def _p_print_dict(dict_):
    for key,val in dict_.items():
        print(key)
        print(val)
        print('\n')

# prints the first n entries in the pandas series, default 5
def preview_series(series, n=5):
    print(series[:n])
    
# appends the key,val pairs in dict_ to the existing dictionary in file_path.
# overwrites the value for key if the key in dict_ is also a key in file_path's dictionary
# TODO: fix update dictionary
def _update_marked_files(file_path, dict_):
    pass
        
# marks the files that might have columns with irregular dtype, e.g. int listed as str
# returns a dictionary: {file_path: (col_name, col_dtype)}
# marks all countries by default
# saves to marked_files.txt by request
def mark_files(dir_, country=None):
    if country:
        group = country
        file_paths = glob(dir_ + '*' + country + '*')
    else:
        group = 'all countries'
        file_paths = _get_tabular_paths_in_dir(dir_)
   
    # record suspect columns
    marked_files = defaultdict(list)
    print('marking dataframes in ' + group + ' with potential incorrect column datatype...')
    for path in file_paths:
        df = read_file_path(path)
        for col_name in df.columns:
            type_ = df[col_name].dtype
            if not _is_valid_type(type_):
                tup = (col_name, type_)
                marked_files[path].append(tup)
    marked_files = dict(marked_files)
    print('finished marking')
    print('marked files: ')
    _p_print_dict(marked_files)
    
    # save the marked files in a txt file if user requests it
    response = input('save marked files to marked_files.txt? ([y]/n)')
    while(response != 'y' and response != 'n' and response != ''):
        response = input('incorrect response. try again: ([y]/n)')
    if response == 'y' or response == '':
        try:
            print('marked_files.txt not found. opening new txt file')
            if not os.path.exists('../public/marked_files.txt'):
                with open('../public/marked_files.txt', 'w+') as file:
                    file.write(str(marked_files))
            else:
                _update_marked_files('../public/marked_files.txt', marked_files)  
        except:
            print('save unsuccessful.')
            raise
        print('finished saving')

# prints all df info in directory unless a country is specified
# dir_ is a path
def summarize(dir_, country=None, sheet=0):
    print('summarizing...')
    try:
        _print_dir_summary(dir_, sheet, country=country)
    except Exception as e: 
        print('unable to summarize')
        raise e
    print('finished summarizing\n')

#TODO: allow for regex grab of paths
def get_file_paths(dir_, regex=False):
    """
    Returns a list of absolute file paths for each file in dir_.

    dir_: String, directory where desired file paths are located
    regex: Boolean, pattern to match while searching
    """
    return glob(dir_ + "*")

