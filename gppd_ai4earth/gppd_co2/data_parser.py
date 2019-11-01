""" 
This file contains support code that will help in parsing a dataset, such
as retrieving a split data set (train, val, test) and others.
"""

import pandas as pd

def train_val_test_split(df, train_percent=0.6, validate_percent=0.2, seed=None):
    """
    Returns a DataFrame tuple of randomly split subsets of the master df set. Randomizes the subsets
    as well to avoid skewing of data. 

    df: DataFrame, the master dataset 
    train_percent: float, percent of examples from df to be allocated to train
    validate_percent: float, percent of examples from df to be allocated to val


    Usage:
    import gppd_co2.data_parser as dp
    train, val, test = dp.train_val_test(df) # df is some pandas DataFrame object

    train, val, test = dp.train_val_test(df, train_percent=0.9, validate_percent=0.05


    Notes:
    The percentages must add up to 100%, otherwise this returns an error. 

    References:
    https://stackoverflow.com/questions/38250710/how-to-split-data-into-3-sets-train-validation-and-test/38251213#38251213
    """
    assert train_percent + validate_percent <= 1, "Argument Error: Invalid percent arguments."
   
    df = df.sample(frac=1, random_state=seed)

    m = len(df.index) # use m to slice the dataset
    train_end = int(train_percent * m)
    validate_end = int(validate_percent * m) + train_end

    train = df.iloc[0:train_end, :].sample(frac=1, random_state=seed)
    test = df.iloc[train_end:validate_end, :].sample(frac=1, random_state=seed)
    val = df.iloc[validate_end:, :].sample(frac=1, random_state=seed)

    return train, test, val

def x_y_split(df, y_label="co2_emissions_tonne"):
    """ Given a dataframe, splits the df into the training X dataset and the true y values using the
    the specified y label name

    Parameters
    df: DataFrame, the dataset to split
    y_label: string, the name of the column that's designated as the true y

    Usage
    X, y = gp.data_parser.x_y_split(df, "co2_emissions_tonne")
    """

    y = df.pop(y_label)
    df = pd.concat([df, y], axis=1) 
    return [df.iloc[:, 0:len(df.columns) - 1], df.iloc[:, len(df.columns) - 1]]
    





    
