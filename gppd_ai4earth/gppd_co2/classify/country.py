""" This file maps countries to their corresponding classification and vice versa using
a bijective dictionary class."""

"""
Workflow:
Goal of this file is to take either a classification (int) or a country code (string) and convert between each other.
Eventually, the user calls a function (say, to_name or to_code) which takes in list-like data structure and loops over each of the members and finally converts them

"""

from os import environ
from gppd_ai4earth.gppd_co2 import obj

# NOTE: this might be an inefficient way. Here, we load the dictionary before we ever use any of the 
# functions. Perhaps load it in the function? But this will load every time we call.
COUNTRY_DICT_PATH = 'C:\\wri_work\\ai4earth_modules\\resources\\dictionaries\\country_classes.txt'#'/home/' + environ['USER'] +  '/public/resources/dictionaries/country_classes.txt'
# wri_workai4earth_modulesresourcesdictionaries

country_dict = obj.load(COUNTRY_DICT_PATH)
country_bijective_dict = obj.BijectiveDict(country_dict)

def to_name(code):
    """ Given an integer classification, converts the code into three character string
    representing the country.

    Parameters
    code: int, a valid integer as defined in country_dict
    """
    assert isinstance(code, int), "ArgumentError: code is not of type int"

    return country_bijective_dict[code]

    
def to_code(name):
    """ Given a name, converts the name to a code as defined in the dictionary
    
    Parameters
    name: string, the three character country name to be converted
    """

    assert isinstance(name, str), "ArgumentError: name is not of type str"

    return country_bijective_dict[name]
