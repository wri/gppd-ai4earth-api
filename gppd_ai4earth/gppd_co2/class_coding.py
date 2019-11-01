import glob
import re
import pandas as pd
import pdb

"""
Note: In order to see edits in this file reflected in a notebook, you must restart your kernel 
so that the notebook imports this module correctly. IPython by default does not reload already imported modules even if
you refresh the page or re-run the cell the module is located at.

Restart the kernel, re-run the cell containing this module import, and you will see your changes.
"""

_FUEL_CODES = {
    'biomass': '1',                                                                                 
    'coal': '2',
    'cogeneration': '3',
    'gas': '4',
    'geothermal': '5',
    'hydro': '6',
    'nuclear': '7',
    'oil': '8',
    'other': '9',
    'petcoke': '10',
    'solar': '11',
    'storage': '12',
    'waste': '13',
    'wave and tidal': '14',
    'wind': '15'
}


# TODO: create a new class called TwoWayDict to avoid
# this data structure
_FUEL_NAMES = {
    '1': 'biomass',
    '2': 'coal',
    '3': 'cogeneration',
    '4': 'gas',
    '5': 'geothermal',
    '6': 'hydro',
    '7': 'nuclear',
    '8': 'oil',
    '9': 'other',
    '10': 'petcoke',
    '11': 'solar',
    '12': 'storage',
    '13': 'waste',
    '14': 'wave and tidal',
    '15': 'wind'
}

def _get_fuel_name(code):
    if pd.isna(code):
        return 'missing'
    return _FUEL_NAMES[str(int(code))]

def _get_fuel_class(fuel):
    """
    This function will search fuel in the fuel thesaurus to find the parent name,
    which are any of the fuels listed in _FUEL_CODES. Then, it returns the associated class for the parent fuel name.
    """

    fuel = fuel.lower()
    thesaurus_collection = glob.glob('../public/resources/fuel_type_thesaurus/*.txt')
    
    for thesaurus in thesaurus_collection:
        pattern = '(.+\/)(.+)\.txt$'
        thesaurus_name = re.search(pattern, thesaurus).group(2).replace('_', ' ')
        with open(thesaurus) as file:
            for candidate_fuel in file:
                candidate_fuel = candidate_fuel.strip().lower()
                
                if fuel == candidate_fuel:
                    fuel_class = code_fuel(thesaurus_name)
                    return fuel_class

def code_fuel(fuel):
    return _FUEL_CODES[fuel]

def map_fuel_codes(dataset, col_name):
    """
    Dataset is a dataframe, col_name is string name for the fuel column
    
    Maps the fuel to its code in place.
    """
    
    fuel_col = dataset[col_name]
    for index, fuel_name in fuel_col.items():
        try:
            if not pd.isna(fuel_name):
                fuel_class = _get_fuel_class(fuel_name)
                dataset.loc[index, col_name] = fuel_class
        except Exception as e:
            raise(e)
            
