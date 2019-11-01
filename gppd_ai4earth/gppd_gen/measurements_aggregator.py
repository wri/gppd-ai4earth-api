from gppd_ai4earth.gppd_gen.geo_utils import MapLocater, BasinDelineator
from gppd_ai4earth.gppd_gen.measurement_files_loader import read_monthly_wind_speed, read_monthly_solar_irradiance, read_monthly_hydro_runoff, HYDRO_BASIN_MEASUREMENTS, HYDRO_RUNOFF_MEASUREMENTS
from itertools import product
import numpy as np
import salem


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
			distances = [d[0] for d in dist_dict]
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
		year = self.formatting_int(year)
		measurements = self.access_or_fetch(year)

		drainage_area, target_polygon_id = self.locater.delineate_basin(lat, lon)
		clipped_measurements = self.clip_roi(measurements, drainage_area)

		results = {}

		target_polygon = drainage_area[drainage_area['HYBAS_ID'] == target_polygon_id]
		for target_polygon_measurement in HYDRO_BASIN_MEASUREMENTS:
			results[target_polygon_measurement] = target_polygon[target_polygon_measurement].values[0]

		for drainage_measurement in HYDRO_RUNOFF_MEASUREMENTS:
			results[drainage_measurement] = np.nansum(np.array(clipped_measurements[drainage_measurement]))

		return results



	def clip_roi(self, array, shape):
		return array.salem.roi(shape = shape)
