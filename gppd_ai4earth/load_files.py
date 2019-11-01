import pandas as pd
import json
from gppd_ai4earth.sources import *

def make_country_names_thesaurus(country_names_thesaurus_file = NAME_THESAURUS_PATH):
    return pd.read_csv(country_names_thesaurus_file,encoding='utf-8')
    

def make_fuel_type_thesaurus(fuel_type_thesaurus_file = FUEL_THESAURUS_PATH):
    return pd.read_csv(fuel_type_thesaurus_file)
    
    # for i in range(data.shape[0]):
    #     country_primary_name = data.loc[i,'primary_country_name']
    #     country_names_thesaurus[country_primary_name] = [
    #             data.loc[i,'geo_country_name'],
    #             data.loc[i,'carma_country_name'],
    #             data.loc[i,'iea_country'],
    #             data.loc[i,'platts_country_name'],
    #             data.loc[i,'oecd_library_country_name']
    #     ]
    # return country_names_thesaurus


def load_combustion_cf(file_path = COUNTRY_CAPACITY_FACTORS_PATH):

    with open(file_path,'r') as file:
        country_cf = json.load(file)

    return country_cf


# def load_total_cap_platts(file_path = TOTAL_CAP_PLATTS_PATH):
#     return pd.read_csv(file_path,encoding='ISO-8859-1')


# def load_total_cap_oecd(file_path = TOTAL_CAP_OECD_PATH):
#     return pd.read_csv(file_path)


def load_renewable_cf(file_path):
    cf_table =  pd.read_csv(file_path)
    return cf_table


def load_wind_cf(file_path = WIND_CF_PATH):
    return load_renewable_cf(file_path)


def load_solar_cf(file_path = SOLAR_CF_PATH):
    return load_renewable_cf(file_path)


def load_hydro_cf(file_path = HYDRO_CF_PATH):
    return load_renewable_cf(file_path)