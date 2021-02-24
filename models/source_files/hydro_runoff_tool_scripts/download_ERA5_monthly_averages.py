"""Download ERA5 monthly averages for precipitation-related fields.

Usage: python <script.py> <CDS_KEY> <SAVE_DIR>
"""
if __name__ == '__main__':
	import argparse
	import cdsapi
	import urllib3
	import os
	import sys

	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


	URL = 'https://cds.climate.copernicus.eu/api/v2'
	KEY = sys.argv[1]  #'6681:96d8ee73-e18c-4f40-a996-82a16404411d'
	RAW_DATA_PATH = os.path.abspath(sys.argv[2])  #os.path.abspath(os.path.join(__file__ ,os.pardir, 'hydro_runoff'))
	FORMAT = 'netcdf'
	VARIABLES = [
		'evaporation',
		'mean_evaporation_rate',
		'mean_runoff_rate',
		'mean_sub_surface_runoff_rate',
		'mean_surface_runoff_rate',
		'mean_total_precipitation_rate',
		'runoff',
		'sub_surface_runoff',
		'surface_runoff',
		'total_precipitation'
	]


	if not os.path.exists(RAW_DATA_PATH):
		os.mkdir(RAW_DATA_PATH)

	for year in range(2013,2018):
		sub_data_path = os.path.join(RAW_DATA_PATH, str(year))

		if not os.path.exists(sub_data_path):
			os.mkdir(sub_data_path)

		c = cdsapi.Client(url=URL, key=KEY)

		str_year = str(year)

		filename = str(year)+ '_monthly_avg' + '.nc'
		filepath = os.path.join(sub_data_path, filename)

		c.retrieve(
			'reanalysis-era5-single-levels-monthly-means',
			{
				'product_type': 'monthly_averaged_reanalysis',
				'format': FORMAT,
				'variable': VARIABLES,
				'year': str_year,
				'month': [
					'01', '02', '03',
					'04', '05', '06',
					'07', '08', '09',
					'10', '11', '12'
				],
				'time': '00:00'
			},
			filepath)

	sys.exit(0)
