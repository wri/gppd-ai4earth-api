import os

__ROOT_PATH = os.getcwd()
__SOURCE_PATH = os.path.join(__ROOT_PATH,'source_files')

def __source_file_path(file_name):
    return os.path.join(__SOURCE_PATH,file_name)

# TOTAL_GEN_PATH = __source_file_path('gen_by_year_country_fuel.json')
# TOTAL_CAP_OECD_PATH = __source_file_path('elecap.csv')
# TOTAL_CAP_PLATTS_PATH = __source_file_path('PLATTS MARCH 2017.csv')
COUNTRY_CAPACITY_FACTORS_PATH = __source_file_path('preprocessed_combustion_capacity_factors.json')

NAME_THESAURUS_PATH = __source_file_path('country_information_updated_v4.csv')
FUEL_THESAURUS_PATH = __source_file_path('fuel_thesaurus.csv')

WIND_CF_PATH = __source_file_path('Wind_Capacity_Factor_Lookup_Table.csv')
SOLAR_CF_PATH = __source_file_path('Solar_Capacity_Factor_Lookup_Table.csv')
HYDRO_CF_PATH = __source_file_path('Hydro_Capacity_Factor_Lookup_Table.csv')

WIND_SPEED_PATH = __source_file_path('wind_speed')
SOLAR_IRRADIANCE_PATH = __source_file_path('solar_irradiance')
HYDRO_BASIN_PATH = __source_file_path('HydroBasins')
HYDRO_RUNOFF_PATH = __source_file_path('hydro_runoff')

GEN_MODEL_PATH = __source_file_path('models')
