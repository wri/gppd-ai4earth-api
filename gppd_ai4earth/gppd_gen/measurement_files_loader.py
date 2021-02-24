from gppd_ai4earth.sources import WIND_SPEED_PATH, SOLAR_IRRADIANCE_PATH, HYDRO_RUNOFF_PATH, HYDRO_BASIN_PATH
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import os

WIND_SPEED_MEASUREMENTS = ['SPEED']
SOLAR_IRRADIANCE_MEASUREMENTS = ['SWGNT', 'TS']
HYDRO_RUNOFF_MEASUREMENTS = ['sro','ssro']
HYDRO_BASIN_MEASUREMENTS = ['ORDER']
CONTINENTS = ['af','ar','as','au','eu','gr','na','sa','si']


def get_files_path_in_dir(directory):
	file_list = os.listdir(directory)
	file_path_list = [os.path.join(directory,f) for f in file_list]
	return file_path_list



def read_measurements_from_netcdf(year, measurements, path):
	'''
	Read netcdf files from disk
	'''
	measurements_dict = {}

	measurements_file_path = os.path.join(path, str(year))
	file_path_list = get_files_path_in_dir(measurements_file_path)

	for measurement in measurements:
		stacked_reads = np.stack([np.array(Dataset(x).variables[measurement][0]) for x in file_path_list])
		averaged_reads = np.mean(stacked_reads, axis = 0)
		measurements_dict[measurement] = averaged_reads
	
	return measurements_dict


def read_measurements_from_xarray(year, path):
	'''
	Read xarray files from disk
	'''
	measurements_file_path = os.path.join(path, str(year))
	file_path_list = get_files_path_in_dir(measurements_file_path)
	return xr.open_dataset(file_path_list[0])


def read_monthly_wind_speed(year):
	return read_measurements_from_netcdf(year, WIND_SPEED_MEASUREMENTS, WIND_SPEED_PATH)


def read_monthly_solar_irradiance(year):
	return read_measurements_from_netcdf(year, SOLAR_IRRADIANCE_MEASUREMENTS, SOLAR_IRRADIANCE_PATH)


def read_monthly_hydro_runoff(year):
	return read_measurements_from_xarray(year, HYDRO_RUNOFF_PATH)


def read_hydro_basin():
	all_basins = pd.DataFrame()

	for c in CONTINENTS:
		print(c)
		path_partial = 'hybas_{0}_lev12_v1c/hybas_{0}_lev12_v1c.shp'.format(c)
		full_path = os.path.join(HYDRO_BASIN_PATH, path_partial)
		all_basins = pd.concat([all_basins, gpd.read_file(full_path)])

	all_basins.reset_index(drop = True, inplace = True)
	all_basins['centroid'] = all_basins['geometry'].apply(lambda x: list(x.centroid.coords)[0])
	all_basins['centroid_lat'] = all_basins['centroid'].apply(lambda x: round(x[1],4))
	all_basins['centroid_lon'] = all_basins['centroid'].apply(lambda x: round(x[0],4))

	return all_basins
