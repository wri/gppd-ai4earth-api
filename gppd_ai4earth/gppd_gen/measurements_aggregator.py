from gppd_ai4earth.gppd_gen.geo_utils import MapLocater, BasinDelineator
from gppd_ai4earth.gppd_gen.measurement_files_loader import read_monthly_wind_speed, read_monthly_solar_irradiance, read_monthly_hydro_runoff, HYDRO_BASIN_MEASUREMENTS, HYDRO_RUNOFF_MEASUREMENTS
from itertools import product
import numpy as np
from rasterio import features
from affine import Affine
import xarray as xr


P = 1

class MeasurementsAggregator:

	'''
	This class calculates the wind speeds and solar irradiance measurements 
	given the location of the wind/solar farm and the year of estimation
	'''

	def __init__(self, locater = MapLocater(), data_reader = read_monthly_wind_speed):
		self.locater = locater
		self.data_reader = data_reader
		self.measurements_dict = {}



	def access_or_fetch(self, year):
		if year not in self.measurements_dict:
			self.measurements_dict[year] = self.data_reader(year)

		return self.measurements_dict[year]



	def formatting_int(self, item):
		return int(item)


	def formatting_str(self, item):
		return str(item)



	def agg_measurements(self, year, lat, lon):
		'''
		This function gets nearby measurements values, 
		interpolate to the exact location of the wind/solar farm and aggregate the measurements into a single value
		'''
		year = self.formatting_int(year)
		measurements = self.access_or_fetch(year)
		dist_dict = self.get_distance_dict(lat,lon)   
		results = {}

		for measurement in list(measurements.keys()):
			values_map = measurements[measurement]
			values = self.indexes_to_values(dist_dict, values_map)
			distances = [0.0001 if d[0] == 0 else d[0] for d in dist_dict]
			results[measurement] = self.idw(distances, values)
		return results



	def indexes_to_values(self, dist_dict, values_map):

		values = []
		for point in dist_dict:
			lat_idx = point[1][0]
			lon_idx = point[1][1]
			values.append(values_map[lat_idx, lon_idx])
		return values



	def idw(self, distances, values):
		'''
		This function performs inverse distance weighted approach to interpolate the measurements of the plant location
		'''
		distances = np.array(distances)
		values = np.array(values)

		idw_numerator = sum(values / (distances**P))
		idw_denominator = sum(1 / (distances**P))
		idw_value = idw_numerator / idw_denominator
		return idw_value
	


	def get_distance_dict(self, lat, lon):
		'''
		This function returns a dictionary that has distance between the plant location to nearby grids
		'''
		(lat_range, lat_index_range),(lon_range, lon_index_range) = self.locater.get_nearby_grids(lat, lon)

		lat_lon_combs = list(product(lat_range,lon_range))
		lat_lon_index_combs = list(product(lat_index_range,lon_index_range))
		lat_lon_zip = list(zip(lat_lon_combs,lat_lon_index_combs))

		dist_dict = []

		for ((nearby_lat, nearby_lon), (nearby_lat_idx, nearby_lon_idx)) in lat_lon_zip:
			dist = np.sqrt((nearby_lat - lat) ** 2 + (nearby_lon - lon) ** 2)
			dist_dict.append([dist,(nearby_lat_idx,nearby_lon_idx),(nearby_lat,nearby_lon)])

		return dist_dict




class HydroRunoffProjector(MeasurementsAggregator):
	'''
	This class calculates the aggreagted runoff value of the hydro basin
	'''
	def __init__(self, locater = BasinDelineator(), data_reader = read_monthly_hydro_runoff):
		super().__init__(locater, data_reader)



	def area_measurements(self, year, lat, lon):

		'''
		This function derives the aggregated runoff measurements
		Inputs: year, lat, lon
		Output: summation of runoff within the drainage area
		'''
		year = self.formatting_int(year)
		measurements = self.access_or_fetch(year)
		drainage_area, target_polygon_id = self.locater.delineate_basin(lat, lon)
		measurements = self.add_shape_coord_from_data_array(measurements, drainage_area['geometry'], "mask")
		cropped_measurements = measurements.where(measurements.mask.notnull(), other=np.nan)

		target_polygon = drainage_area[drainage_area['HYBAS_ID'] == target_polygon_id]
		results = {}

		for target_polygon_measurement in HYDRO_BASIN_MEASUREMENTS:
			results[target_polygon_measurement] = target_polygon[target_polygon_measurement].values[0]

		for drainage_measurement in HYDRO_RUNOFF_MEASUREMENTS:
			results[drainage_measurement] = np.nansum(cropped_measurements[drainage_measurement])

		return results


	def transform_from_latlon(self, lat, lon):
		""" input 1D array of lat / lon and output an Affine transformation
		"""
		lat = np.asarray(lat)
		lon = np.asarray(lon)
		trans = Affine.translation(lon[0], lat[0])
		scale = Affine.scale(lon[1] - lon[0], lat[1] - lat[0])
		return trans * scale



	def rasterize(self, shapes, coords, latitude='lat', longitude='lon',
				  fill=np.nan, **kwargs):
		'''Rasterize a list of (geometry, fill_value) tuples onto the given
		xray coordinates. This only works for 1d latitude and longitude
		arrays.
		'''
		transform = self.transform_from_latlon(coords[latitude], coords[longitude])
		out_shape = (len(coords[latitude]), len(coords[longitude]))
		raster = features.rasterize(shapes, out_shape=out_shape,
									fill=fill, transform=transform,
									dtype=float, **kwargs)
		spatial_coords = {latitude: coords[latitude], longitude: coords[longitude]}
		return xr.DataArray(raster, coords=spatial_coords, dims=(latitude, longitude))



	def add_shape_coord_from_data_array(self, xr_da, shp_gpd, coord_name):
		''' Create a new coord for the xr_da indicating whether or not it 
			 is inside the shapefile

			Creates a new coord - "coord_name" which will have integer values
			 used to subset xr_da for plotting / analysis/
		'''

		shapes = [(shape, n) for n, shape in enumerate(shp_gpd.geometry)]
		xr_da[coord_name] = self.rasterize(shapes, xr_da.coords, 
								   longitude='lon', latitude='lat')

		return xr_da
