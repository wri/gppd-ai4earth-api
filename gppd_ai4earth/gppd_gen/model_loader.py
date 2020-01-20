from gppd_ai4earth.sources import GEN_MODEL_PATH
import pickle
import os

MODEL_NAME_PREFIX = 'ai4e_'
WIND_MODEL = 'wind_model.sav'
SOLAR_MODEL = 'solar_model.sav'
HYDRO_MODEL = 'hydro_model.sav'
GAS_MODEL = 'gas_model.sav'
SOLAR_MODEL_NO_AGE = 'solar_model_no_age.sav'

def __model_full_path(model_name, path = GEN_MODEL_PATH):
	return os.path.join(path, model_name)

def __load_model(full_path):
	with open(full_path, 'rb') as file:
		model = pickle.load(file)
	return model

def __parse_model_name(file_name):
	return MODEL_NAME_PREFIX + file_name.split('.')[0]

def load_wind_model():
	return __load_model(__model_full_path(WIND_MODEL)), __parse_model_name(WIND_MODEL)

def load_solar_model():
	return __load_model(__model_full_path(SOLAR_MODEL)), __parse_model_name(SOLAR_MODEL)

def load_solar_model_no_age():
	return __load_model(__model_full_path(SOLAR_MODEL_NO_AGE)), __parse_model_name(SOLAR_MODEL_NO_AGE)

def load_hydro_model():
	return __load_model(__model_full_path(HYDRO_MODEL)), __parse_model_name(HYDRO_MODEL)

def load_gas_model():
	return __load_model(__model_full_path(GAS_MODEL)), __parse_model_name(GAS_MODEL)