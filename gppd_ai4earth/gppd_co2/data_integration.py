#!/usr/bin/env python
# coding: utf-8
"""
This file contains functions that helps integrating data together 
in a variety of folders, such as creating a master training dataset from
the various countries.
"""
import gppd_ai4earth.gppd_co2.dfreader as dfr
import pandas as pd
from pathlib import Path

def make_master_df(dir_):
    """ Given a directory path, concatenates data into one master data
    set and returns the dataset as a dataframe.
    
    dir_: String, the absolute or relative directory path containing the
        data sets
    """
   
    try:
        paths = dfr.get_file_paths(dir_)
    except:
        print("Directory does not exist: ", dir_)

    df_list = [dfr.read_file_path(path) for path in paths]
    concat_df = pd.concat(df_list, sort=False)
    return concat_df

def save_data(dataset, filename, dir_):
    """
    Parameters
    dataset: pandas DataFrame or Series
    filename: String, the name of the file name, not including its path
    dir_: String, the directory where the dataset will be saved to. Must include '/' at the end
    
    Usage
    save_data(df, "medical_info.csv", "home/user/")
    """
    dataset.to_csv(Path(dir_, filename), index=False)
    
    

