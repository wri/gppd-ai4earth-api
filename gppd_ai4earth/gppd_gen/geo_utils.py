from gppd_ai4earth.gppd_gen.measurement_files_loader import read_hydro_basin
import numpy as np
import geopandas as gpd
from shapely import geometry
import pandas as pd

class MapLocater:
	
	
	def __init__(self, dim=(3,3)):
		self.lat_interval = 0.5
		self.lon_interval = 0.625
		
		self.lats = list(np.linspace(-90,90,361))
		self.lons = list(np.linspace(-180,179.375,576))

		self.lat_dim, self.lon_dim = dim



	def get_nearby_grids(self, lat, lon):

		'''
		This function calculates the closest corrdinates given the lat and lon of an arbitrary location
		lat: The latitude of the location
		lon: The longitude of the location
		Return: (a latitude lists containing latitude of the closest points, associated indexes of these latitude values),
		(a longitude lists containing longitude of the closest points, associated indexes of these longitude values)
		'''
		closest_lats = self.get_closest_lats(lat)
		closest_lons = self.get_closest_lons(lon)
		closets_lats_index, closest_lons_index = self.nearbyGridsIndex(closest_lats, closest_lons)

		return (closest_lats, closets_lats_index), (closest_lons, closest_lons_index)
	


	def nearbyGridsIndex(self, closest_lats, closest_lons):
		lat_range_index = [self.lats.index(lat) for lat in closest_lats]
		lon_range_index = [self.lons.index(lon) for lon in closest_lons]
		
		return lat_range_index, lon_range_index
		


	def get_closest_lats(self, lat):
		return self.get_closest_points(lat,
			self.lats, 
			self.lat_interval, 
			self.valid_latitude, 
			self.lat_dim)


	
	def get_closest_lons(self, lon):
		return self.get_closest_points(lon, 
			self.lons, 
			self.lon_interval, 
			self.valid_longitude, 
			self.lon_dim)



	def get_closest_points(self, v, vs, interval, clipper, dim):
		'''
		This function returns dim points in vs that are closest to v
		v: The target point
		vs: The range where closest points are searched in
		interval: The interval between points along this axis
		clipper: The function that ensures the derived values are valid longitude and latitude
		dim: The number of closest points along longitude and latitude
		'''
		lower_bound = self.get_lower_bound(v,vs)
		upper_bound = lower_bound + interval

		closest_points = []
		for i in range(dim):

			if self.lower_is_closer(v, lower_bound, upper_bound):
				closest_points.append(clipper(lower_bound))
				lower_bound -= interval
			else:
				closest_points.append(clipper(upper_bound))
				upper_bound += interval

		closest_points = list(set(closest_points))

		return closest_points



	def lower_is_closer(self, target, lower, upper):
		'''
		Check if target is closer to the lower bound or the upper bound
		'''
		return (target - lower) <= (upper - target)




	def valid_longitude(self, lon):
		'''
		Make sure the longitude is a valid one. If not, convert it to a valid one.
		lon: The longitude to be checked
		'''
		if lon > self.lons[-1]:
			return self.lons[0] + (lon - self.lons[-1]) - self.lon_interval

		if lon < self.lons[0]:
			return self.lons[-1] - (self.lons[0] - lon) + self.lon_interval

		return lon


	def valid_latitude(self, lat):
		'''
		Make sure the latitude is a valid one. If not, convert it to a valid one.
		lat: The latitude to be checked
		'''
		if lat > self.lats[-1]:
			return self.lats[-1] - (lat - self.lats[-1])

		if lat < self.lats[0]:
			return self.lats[-1] + (self.lons[0] - lat)

		return lat

	
	def get_lower_bound(self, v, vs):
		'''
		Find the lower closest coordinates
		v: The target value
		vs: The range of coordinates
		'''
		l = len(vs)
		start = 0
		end = l - 1

		if v >= vs[end]:
			return vs[end]

		while(start + 1 < end):
			mid = (start + end) // 2

			if vs[mid] <= v:
				start = mid
			elif vs[mid] > v:
				end = mid

		if vs[end] <= v:
			return vs[end]
		if vs[start] <= v:
			return vs[start]





class BasinDelineator:
	
	
	def __init__(self):

		'''
		shape_file_path: Path to the shape file.

		nc_file_folder: Directory to the folder where the relevant netcdf files are stored

		variables: A list of selected netcdf file variables. If None, all variables where be aggregated

		'''
		self.geodf = None
		


	def delineate_basin(self, lat, lon):
		self.check_geodf_existance()

		target_polygon_id = self.get_target_polygon(lat, lon)
		if not target_polygon_id:
			return False

		drainage_area = self.get_drainage_polygons_bfs(target_polygon_id)
		return drainage_area, target_polygon_id



	def rank_candidate_by_dist(self,lat,lon):
		self.geodf['temp_distance'] = np.sqrt((self.geodf['centroid_lat'] - lat) ** 2 + (self.geodf['centroid_lon'] - lon) ** 2)
		return self.geodf.sort_values('temp_distance').head(100)
		
		
		
	def get_target_polygon(self,lat,lon):
		candidates = self.rank_candidate_by_dist(lat,lon)
		
		point = geometry.Point(lon,lat)
		for basin_id in candidates['HYBAS_ID']:
			
			candidate_polygon = candidates.loc[candidates['HYBAS_ID'] == basin_id, 'geometry'].values[0]
			if candidate_polygon.contains(point):
				return basin_id

		return False
				
	

	def check_geodf_existance(self):
		if self.geodf is None:
			self.geodf = read_hydro_basin()



	def get_drainage_polygons_bfs(self, target_polygon_id):
		
		results = []
		queue = []
		visited = set()
		results.append(target_polygon_id)
		queue.append(target_polygon_id)
		visited.add(target_polygon_id)

		while(len(queue) > 0):

			cur_node = queue.pop(0)
			next_nodes = self.geodf.loc[self.geodf['NEXT_DOWN']==cur_node,'HYBAS_ID'].values

			for next_node in next_nodes:
				if next_node in visited:
					continue

				results.append(next_node)
				queue.append(next_node)
				visited.add(next_node)
		
		drainage_polygons = self.geodf[self.geodf['HYBAS_ID'].isin(results)]
		return drainage_polygons
