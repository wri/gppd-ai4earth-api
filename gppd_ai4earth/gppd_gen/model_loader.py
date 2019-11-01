from gppd_ai4earth.sources import GEN_MODEL_PATH
import pickle
import os

WIND_MODEL = 'wind_model.sav'
SOLAR_MODEL = 'solar_model.sav'
HYDRO_MODEL = 'hydro_model.sav'
GAS_MODEL = 'gas_model.sav'

def __model_full_path(model_name, path = GEN_MODEL_PATH):
	return os.path.join(path, model_name)

def __load_model(full_path):
	with open(full_path, 'rb') as file:
		model = pickle.load(file)
	return model

def load_wind_model():
	return __load_model(__model_full_path(WIND_MODEL))

def load_solar_model():
	return __load_model(__model_full_path(SOLAR_MODEL))

def load_hydro_model():
	return __load_model(__model_full_path(HYDRO_MODEL))

def load_gas_model():
	return __load_model(__model_full_path(GAS_MODEL))