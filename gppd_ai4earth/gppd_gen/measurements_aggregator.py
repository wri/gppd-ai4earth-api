from gppd_ai4earth.gppd_gen.geo_utils import MapLocater, BasinDelineator
from gppd_ai4earth.gppd_gen.measurement_files_loader import read_monthly_wind_speed, read_monthly_solar_irradiance, read_monthly_hydro_runoff, HYDRO_BASIN_MEASUREMENTS, HYDRO_RUNOFF_MEASUREMENTS
from itertools import product
import numpy as np
from rasterio import features
from affine import Affine
import xarray as xr
# import salem


P = 1

class MeasurementsAggregator:


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
		year = self.formatting_int(year)

		measurements = self.access_or_fetch(year)

		dist_dict = self.get_distance_dict(lat,lon)   
		#schema of distances [dist, (lat_index,lon_index), (lat, lon)]
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

		distances = np.array(distances)
		values = np.array(values)

		idw_numerator = sum(values / (distances**P))
		idw_denominator = sum(1 / (distances**P))
		idw_value = idw_numerator / idw_denominator
		return idw_value
	


	def get_distance_dict(self, lat, lon):

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

	def __init__(self, locater = BasinDelineator(), data_reader = read_monthly_hydro_runoff):
		super().__init__(locater, data_reader)
		#locater = BasinDelineator()  (lat, lon) -> subset of geodf with polygons, target_polygon_id
		#self.data_reader = read_monthly_hydro_runoff -> xarray
		#self.measurements_dict = {}



	def area_measurements(self, year, lat, lon):
		# print('In func area_measurements')
		year = self.formatting_int(year)

		# print('In func area_measurements: fetch monthly hydro runoff')
		measurements = self.access_or_fetch(year)

		# print('In func area_measurements: delineate basin')
		drainage_area, target_polygon_id = self.locater.delineate_basin(lat, lon)

		# print(measurements)
		# print(drainage_area)

		# print('In func area_measurements: clip roi')
		measurements = self.add_shape_coord_from_data_array(measurements, drainage_area['geometry'], "mask")
		cropped_measurements = measurements.where(measurements.mask.notnull(), other=np.nan)

		target_polygon = drainage_area[drainage_area['HYBAS_ID'] == target_polygon_id]
		results = {}

		for target_polygon_measurement in HYDRO_BASIN_MEASUREMENTS:
			results[target_polygon_measurement] = target_polygon[target_polygon_measurement].values[0]

		for drainage_measurement in HYDRO_RUNOFF_MEASUREMENTS:
			results[drainage_measurement] = np.nansum(cropped_measurements[drainage_measurement])

		# print('In func area_measurements: {}'.format(results))
		return results



	# def clip_roi(self, array, shape):
	# 	return array.salem.roi(shape = shape)



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
		"""Rasterize a list of (geometry, fill_value) tuples onto the given
		xray coordinates. This only works for 1d latitude and longitude
		arrays.

		arguments:
		---------
		: **kwargs (dict): passed to `rasterio.rasterize` function

		attrs:
		-----
		:transform (affine.Affine): how to translate from latlon to ...?
		:raster (numpy.ndarray): use rasterio.features.rasterize fill the values
		  outside the .shp file with np.nan
		:spatial_coords (dict): dictionary of {"X":xr.DataArray, "Y":xr.DataArray()}
		  with "X", "Y" as keys, and xr.DataArray as values

		returns:
		-------
		:(xr.DataArray): DataArray with `values` of nan for points outside shapefile
		  and coords `Y` = latitude, 'X' = longitude.


		"""
		transform = self.transform_from_latlon(coords[latitude], coords[longitude])
		out_shape = (len(coords[latitude]), len(coords[longitude]))
		raster = features.rasterize(shapes, out_shape=out_shape,
									fill=fill, transform=transform,
									dtype=float, **kwargs)
		spatial_coords = {latitude: coords[latitude], longitude: coords[longitude]}
		return xr.DataArray(raster, coords=spatial_coords, dims=(latitude, longitude))



	def add_shape_coord_from_data_array(self, xr_da, shp_gpd, coord_name):
		""" Create a new coord for the xr_da indicating whether or not it 
			 is inside the shapefile

			Creates a new coord - "coord_name" which will have integer values
			 used to subset xr_da for plotting / analysis/

			Usage:
			-----
			precip_da = add_shape_coord_from_data_array(precip_da, "awash.shp", "awash")
			awash_da = precip_da.where(precip_da.awash==0, other=np.nan) 
		"""
		# 1. read in shapefile
	#     shp_gpd = gpd.read_file(shp_path)

		# 2. create a list of tuples (shapely.geometry, id)
		#    this allows for many different polygons within a .shp file (e.g. States of US)
		shapes = [(shape, n) for n, shape in enumerate(shp_gpd.geometry)]

		# 3. create a new coord in the xr_da which will be set to the id in `shapes`
		xr_da[coord_name] = self.rasterize(shapes, xr_da.coords, 
								   longitude='lon', latitude='lat')

		return xr_da
