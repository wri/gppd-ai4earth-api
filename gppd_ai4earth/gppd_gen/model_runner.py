from gppd_ai4earth.gppd_gen import model_loader
from gppd_ai4earth import capacity_factor_retriever
from gppd_ai4earth.gppd_gen import measurements_aggregator
from gppd_ai4earth.gppd_gen.measurement_files_loader import *
import numpy as np


VALID_FUEL_TYPES = ['Wind', 'Solar', 'Hydro', 'Gas']


WIND_PARAM_LIST = {'capacity_mw': (int,float), 'estimating_year': int, 'commissioning_year': (int,float), 'country': str, 'fuel_type': str, 'lat': (int,float), 'lon': (int,float)}
SOLAR_PARAM_LIST = {'capacity_mw': (int,float), 'estimating_year': int, 'commissioning_year': (int,float), 'country': str, 'fuel_type': str, 'lat': (int,float), 'lon': (int,float)}
HYDRO_PARAM_LIST = {'capacity_mw': (int,float), 'estimating_year': int, 'country': str, 'fuel_type': str, 'lat': (int,float), 'lon': (int,float)}
GAS_PARAM_LIST = {'capacity_mw': (int,float), 'estimating_year': int, 'commissioning_year': (int,float), 'country': str, 'fuel_type': str, 'turbine_type': str}
GAS_TURBINE_TYPES = ['CCGT','CS','FC','GT','IC','ST']


PARAMETER_LISTS = {
	'Wind': WIND_PARAM_LIST,
	'Solar': SOLAR_PARAM_LIST,
	'Hydro': HYDRO_PARAM_LIST,
	'Gas': GAS_PARAM_LIST
}
	


class Estimator:

	'''
	This Estimator class takes in power plant parameters and deliver generation estimations using machine learning models
	'''

	def __init__(self):
		self.models = {}
		self.cf_getter = capacity_factor_retriever.AvgCapacityFactorRetriever()
		self.natural_resources_getters = {}
		self.messages = {
			'fuel_type_error': 'Fuel_type_not_found.',
			'available_fuel_types': 'Available fuel types are {}.'.format(', '.join(VALID_FUEL_TYPES)),
			'fuel_type_missing': 'Please specify a fuel_type to proceed the generation estimation.',
			'year error': 'estimating_year cannot be earlier than commissioning_year',
			'lat_error': 'tatitude should be with the range [-90,90]',
			'lon_error': 'tongitude should be with the range [-180, 180]',
			'turbine_type_error_message': 'turbine_type should be one of {}'.format(', '.join(GAS_TURBINE_TYPES)) 
		}
		self.feature_func_by_fuel = {
			'Wind': self.wind_feature_transformation(),
			'Solar': self.solar_feature_transformation(),
			'Gas': self.gas_feature_transformation(),
			'Hydro': self.hydro_feature_transformation()
		}
		self.natural_resource_loader = {
			'Wind': read_monthly_wind_speed,
			'Solar': read_monthly_solar_irradiance,
			'Hydro': read_monthly_hydro_runoff
		}



	def wind_feature_transformation(self):
		'''
		The wind_feature_transformation function transforms raw fields into features 
		that the machine learning models are trained on.
		'''
		def inner_func(all_features):
			
			country = all_features['country']
			capacity_mw = all_features['capacity_mw']
			estimating_year = all_features['estimating_year']
			commissioning_year = all_features['commissioning_year']
			fuel_type = all_features['fuel_type']
			lat = all_features['lat']
			lon = all_features['lon']
			self.lat_lon_check(lat, lon)

			country_capacity_factor = self.cf_getter.retrieve_capacity_factor(estimating_year, country, fuel_type)
			age = self.get_age(estimating_year, commissioning_year)
			aggregator = self.get_or_load_natural_resources_getter(fuel_type)
			avg_wind_speed = aggregator.agg_measurements(estimating_year, lat, lon)

			return np.array([capacity_mw, age, country_capacity_factor, avg_wind_speed['SPEED']])[np.newaxis,:]

		return inner_func



	def solar_feature_transformation(self):
		'''
		The wind_feature_transformation function transforms raw fields into features 
		that the machine learning models are trained on.
		'''
		def inner_func(all_features):

			country = all_features['country']
			capacity_mw = all_features['capacity_mw']
			estimating_year = all_features['estimating_year']

			commissioning_year = np.NaN
			if 'commissioning_year' in all_features:
				commissioning_year = all_features['commissioning_year']

			fuel_type = all_features['fuel_type']
			lat = all_features['lat']
			lon = all_features['lon']
			self.lat_lon_check(lat, lon)

			country_capacity_factor = self.cf_getter.retrieve_capacity_factor(estimating_year, country, fuel_type)

			age = np.NaN
			if not np.isnan(commissioning_year):
				age = self.get_age(estimating_year, commissioning_year)

			aggregator = self.get_or_load_natural_resources_getter(fuel_type)
			avg_solar_irradiance = aggregator.agg_measurements(estimating_year, lat, lon)

			return np.array([capacity_mw, age, country_capacity_factor, avg_solar_irradiance['TS'], avg_solar_irradiance['SWGNT']])[np.newaxis,:]

		return inner_func



	def gas_feature_transformation(self):
		'''
		The gas_feature_transformation function transforms raw fields into features 
		that the machine learning models are trained on.
		'''
		def inner_func(all_features):

			country = all_features['country']
			capacity_mw = all_features['capacity_mw']
			estimating_year = all_features['estimating_year']
			commissioning_year = all_features['commissioning_year']
			fuel_type = all_features['fuel_type']
			turbine_type = all_features['turbine_type']
			self.turbine_type_check(turbine_type)

			country_capacity_factor = self.cf_getter.retrieve_capacity_factor(estimating_year, country, fuel_type)
			age = self.get_age(estimating_year, commissioning_year)

			turbine_type_onehot = [0] * len(GAS_TURBINE_TYPES)
			one_hot_index = GAS_TURBINE_TYPES.index(turbine_type)
			turbine_type_onehot[one_hot_index] = 1

			return np.array([capacity_mw, age, country_capacity_factor] + turbine_type_onehot)[np.newaxis,:]

		return inner_func



	def hydro_feature_transformation(self):
		'''
		The wind_feature_transformation function transforms raw fields into features 
		that the machine learning models are trained on.
		'''
		def inner_func(all_features):

			country = all_features['country']
			capacity_mw = all_features['capacity_mw']
			estimating_year = all_features['estimating_year']
			fuel_type = all_features['fuel_type']
			lat = all_features['lat']
			lon = all_features['lon']
			self.lat_lon_check(lat, lon)

			country_capacity_factor = self.cf_getter.retrieve_capacity_factor(estimating_year, country, fuel_type)

			projector = self.get_or_load_natural_resources_getter(fuel_type)

			hydro_indicators = projector.area_measurements(estimating_year, lat, lon)

			return np.array([capacity_mw, 
							 country_capacity_factor, 
							 hydro_indicators['sro'], 
							 hydro_indicators['ssro'],
							 hydro_indicators['ORDER']])[np.newaxis,:]

		return inner_func

	

	def turbine_type_check(self, turbine_type):
		'''
		This function checks if the turbine type is a valid one.
		'''
		assert turbine_type in GAS_TURBINE_TYPES, self.messages['turbine_type_error_message']



	def lat_lon_check(self, lat, lon):
		'''
		This function checks if the coordinates are valid ones.
		'''
		assert lat >= -90 and lat <= 90, self.messages['lat_error']
		assert lon >= -180 and lon <= 180, self.messages['lon_error']



	def get_age(self, estimating_year, commissioning_year):
		'''
		This function checks if the commissioning year is earlier than the estimating year,
		and returns the age if pass the screen.
		'''
		assert commissioning_year < estimating_year, self.messages['year error']
		return estimating_year - commissioning_year



	def get_or_load_natural_resources_getter(self, fuel_type):
		'''
		Get the resources(wind speeds, solar irradiances and hydro runoff) reader from the memory. If the reader is not loaded, 
		load the reader from the disk and persist in the memory for fast access.
		'''
		if fuel_type not in self.natural_resources_getters:
			reader = self.get_measurements_loader(fuel_type)
			self.natural_resources_getters[fuel_type] = self.get_measurements_processor(fuel_type, reader)

		return self.natural_resources_getters[fuel_type]



	def get_measurements_loader(self, fuel_type):
		'''
		This function returns functions that load natural resource measurements
		given fuel type.
		'''
		return self.natural_resource_loader[fuel_type]



	def get_measurements_processor(self, fuel_type, reader):
		'''
		This function loads natural resources processor depending on the fuel type 
		(wind and solar share the same processor, and hydro has its own processor)
		'''
		if fuel_type == 'Hydro':
			return measurements_aggregator.HydroRunoffProjector(data_reader = reader)
		else:
			return measurements_aggregator.MeasurementsAggregator(data_reader = reader)



	def get_or_load_model(self, fuel_type):
		'''
		Get the trained machine learning models from the memory. If the model is not loaded, 
		load the model from the disk and persist in the memory for fast access.
		'''
		if fuel_type not in self.models:
			model, model_name = self.load_model(fuel_type)
			self.models[fuel_type] = {'model':model, 'model_name':model_name}
		return self.models[fuel_type]['model'], self.models[fuel_type]['model_name']



	def load_model(self, fuel_type):
		'''
		This function calls the model loader according to the fuel type.
		'''
		if fuel_type == 'Wind':
			return model_loader.load_wind_model()

		if fuel_type == 'Solar':
			return model_loader.load_solar_model()

		if fuel_type == 'Solar_no_age':
			return model_loader.load_solar_model_no_age()

		if fuel_type == 'Hydro':
			return model_loader.load_hydro_model()

		if fuel_type == 'Gas':
			return model_loader.load_gas_model()



	def parameter_sanity_check(self, fuel_type, parameter_dict):
		'''
		This functions checks parameters existance and parameter types according to the fuel type.
		'''
		check_list = PARAMETER_LISTS[fuel_type]
		missing_params = []
		params_type_errors = {}

		for param, p_type in check_list.items():

			if param not in parameter_dict:
				missing_params.append(param)

			else:
				if not isinstance(parameter_dict[param], p_type):
					params_type_errors[param] = p_type

		if fuel_type == 'Solar' and len(missing_params) == 1 and missing_params[0] == 'commissioning_year':
			pass
		else:
			assert len(missing_params) == 0, 'Missing parameters: {}'.format(', '.join(missing_params))
			assert len(params_type_errors) == 0, '\n'.join(["Parameter {}'s type not match: {} required".format(p, t) for p,t in params_type_errors.items()])



	def estimates(self, **kwargs):
		'''
		This function takes in a dictionary of power plant paramters and returns generation estimation and the model name as a tuple
		
		Inputs:
		Wind -> fuel_type, capacity_mw, estimating_year, commissioning_year, country, lat, lon
		Solar -> fuel_type, capacity_mw, estimating_year, commissioning_year(optional), country, lat, lon
		Hydro -> fuel_type, capacity_mw, estimating_year, country, lat, lon
		Gas -> fuel_type, capacity_mw, estimating_year, commissioning_year, turbine_type, country, lat, lon

		Output: (generation, model name)
		'''
		assert 'fuel_type' in kwargs, self.messages['fuel_type_missing'] + '\n' + self.messages['available_fuel_types']
		assert kwargs['fuel_type'] in VALID_FUEL_TYPES, self.messages['fuel_type_error'] + '\n' + self.messages['available_fuel_types']

		fuel_type = kwargs['fuel_type']
		self.parameter_sanity_check(fuel_type, kwargs)

		final_features = self.feature_transformation(fuel_type, kwargs)

		if fuel_type == 'Solar' and np.isnan(final_features[0][1]):
			final_features = np.delete(final_features, 1, 1)
			model, model_name = self.get_or_load_model(fuel_type + '_no_age')
		else:
			model, model_name = self.get_or_load_model(fuel_type)

		if (np.isnan(final_features).any()):
			return np.NaN

		return model.predict(final_features)[0], model_name



	def feature_transformation(self, fuel_type, all_features):
		'''
		This function transform fields into features that will be used in the machine learning models.
		'''
		relevant_parameters = PARAMETER_LISTS[fuel_type].copy()
		if fuel_type == 'Solar' and 'commissioning_year' not in all_features:
			del relevant_parameters['commissioning_year']
		relevant_features = {k:all_features[k] for k,v in relevant_parameters.items()}
		return self.feature_func_by_fuel[fuel_type](relevant_features)




