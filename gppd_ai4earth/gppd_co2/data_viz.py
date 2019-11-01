
"""
This file contains functions that will be useful in understanding data located in public/.
This includes visualization functions, statistics, and others.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import gppd_ai4earth.gppd_co2.dfreader as dfr
import gppd_ai4earth.gppd_co2.class_coding as cc
import pdb
import pandas as pd
import numpy as np
sns.set()
from collections import defaultdict
from decimal import Decimal

""" Constants """
TITLE_Y_OFFSET = 18
""""""


# TODO: this function needs some major efficiency updates. if fuel
# types are specified, takes a long time since we are looping through
# each row in the dataset.
def plot_scatter(dataframe, x_col_name, y_col_name, x_label=None, y_label=None, scatter_title="Scatter Plot",
                 x_left=None, x_right=None, y_bot=None, y_top=None, fuels_to_plot=[]):
    """
    Given a dataframe, plots a scatter plot of the two columns,
    which will be located on the x,y axis respectively.

    Can also plot specific fuel types if given a list fuel types.
    """
    # if no labels were provided, the default will be the column names as labels
    if not x_label:
        x_label = x_col_name
    if not y_label:
        y_label = y_col_name

    if x_left:
        plt.xlim(left=x_left)
    if x_right:
        plt.xlim(right=x_right)
    if y_bot:
        plt.ylim(bottom=y_bot)
    if y_top:
        plt.ylim(top=y_top)

    # plot a column against co2 emissions if left as default, else plot specific fuel types of the dataset
    if not fuels_to_plot:    
        sns.lmplot( x=x_col_name, y=y_col_name, data=dataframe, fit_reg=False, hue='primary_fuel', legend=False)
    else:
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        
        # plot x against y by fuel type on the same figure
        for fuel in fuels_to_plot:
            x_col = []
            y_col = []


            # TODO: make this more efficient
            for index, row in dataframe.iterrows():
                row_fuel_name = row['primary_fuel']
                if row_fuel_name == fuel:
                    x_col.append(row[x_col_name])
                    y_col.append(row[y_col_name])

            plt.plot(x_col, y_col, marker='o', label=fuel, linestyle='None')
            
    plt.legend(loc='best')
    plt.title(scatter_title, pad=TITLE_Y_OFFSET)
    plt.show()

def plot_stats(file_path, exclude=[], fuels_to_plot=[], y_col_name='co2_emissions_tonne'):
    """
    Plots statistics for trainable dataframe located in file_path
    
    file_path: string, absolute location of the file including the file itself
    exclude: list of column names to exclude creating scatter plots
    fuel_types: list of fuel type names for which stats will be reported on. if more than one are
           specified, colors will be used to demarcate the different fuel types
    y_col_name: column to be compared against. co2 emissions by default
    """

    ''''''
    def get_unreported(dataset):
        num_plants = len(dataset.index)
        count_col = dataset.count()
        unreported = [num_plants - reported for reported in count_col]
        return unreported

    # might delete this later since function below does the same thing
    # but also provides proportion of counts by fuel type
    def get_zeros(dataset):
        report = ['co2_emissions_tonne', 'capacity_mw', 'generation_gwh']
     
        zeros = []
        for col_name in dataset.columns:
            if col_name in report:
                zero_count = 0
                for val in dataset[col_name]:
                    if val == 0:
                        zero_count += 1
                zeros.append(zero_count)
            else:
                zeros.append('N/A')
        return zeros

    def print_zeros_by_fuel_type(dataset):
        report = ['co2_emissions_tonne', 'capacity_mw', 'generation_gwh']

        # each key is the column name in report, and the value is a dictionary of counts 
        # by fuel type. used to compute proportions of zero values by fuel type
        col_zero_proportions = defaultdict(dict)
        for col_name in dataset:
            if col_name in report:
                
                # populate dictionary with number of zero values by fuel type
                fuel_zero_proportions = defaultdict(int)
                for index, val in dataset[col_name].items():
                    if val == 0:
                        fuel_code =  dataset.loc[index, 'primary_fuel']
                        fuel_name = cc._get_fuel_name(fuel_code)
                        fuel_zero_proportions[fuel_name] += 1
                        
                # use this dictionary as a value for the column name in report
                col_zero_proportions[col_name] = fuel_zero_proportions

        print('number of values that are zero by primary_fuel')
        for col_name, counts in sorted(col_zero_proportions.items()):
            # column name
            # total: num zeros
            # fuel_1: num zeros that are fuel_1
            # ...
            total = sum(col_zero_proportions[col_name].values())
            print(col_name)
            print('total: ', total)
            fuel_zero_proportions = col_zero_proportions[col_name]
            for fuel_name in fuel_zero_proportions:
                dec = Decimal(100 * fuel_zero_proportions[fuel_name] / float(total))
                print(fuel_name, ': ', round(dec, 2), '%')
            print('\n')

        
    ''''''
        
    df = dfr.read_file_path(file_path) 
    data = {'count':df.count(), 'min':df.min(), 'max':df.max(), 'mean':df.mean(), 
            'count_unreported': get_unreported(df), 'count_zero_values':get_zeros(df)}
    print(pd.DataFrame(data=data))
    print('\n')
    
    #TODO: fix how this looks like when printed
    print('total num examples:       ', len(df.index))
    for label, count in df['primary_fuel'].value_counts(dropna=False).items():
        code_name = cc._get_fuel_name(label)
        print('count examples ' + code_name + '    ' + str(count))
    print('\n')

    print_zeros_by_fuel_type(df)

    df['primary_fuel'] = df['primary_fuel'].apply(cc._get_fuel_name)
    for col_name in df.columns:
        if col_name == y_col_name or col_name in exclude:
            continue
        title = col_name + ' vs ' + y_col_name
        plot_scatter(df, col_name, y_col_name, scatter_title=title, fuels_to_plot=fuels_to_plot)
