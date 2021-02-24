"""Quick and dirty testing, non-exhaustive and without a framework."""
import requests
import json
from time import sleep
import os

BASE_URL = 'http://localhost:5151/v1/my_api/tasker/'
TEST_URL = BASE_URL + 'test'  # sync
ECHO_URL = BASE_URL + 'echo/'  # sync
ESTIMATE_URL = BASE_URL + 'estimate'  # async
TASK_STATUS_URL = BASE_URL + 'task/'  # sync
BASELINE_URL = BASE_URL + 'baseline'  # sync

TEST_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
MODEL_DIR = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, 'models'))
SOURCE_FILES_DIR = os.path.abspath(os.path.join(MODEL_DIR, 'source_files'))

HYDRO_BASINS_DIR = os.path.abspath(os.path.join(SOURCE_FILES_DIR, 'HydroBasins'))
HYDRO_BASINS_CONTINENT_FMT = 'hybas_{0}_lev12_v1c'
HYDRO_BASINS_CONTINENTS = ['af', 'ar', 'as', 'au', 'eu', 'gr', 'na', 'sa', 'si']

HYDRO_RUNOFF_DIR = os.path.abspath(os.path.join(SOURCE_FILES_DIR, 'hydro_runoff'))
HYDRO_RUNOFF_FMT = '{0}/{0}_monthly_avg_transformed.nc'
HYDRO_RUNOFF_YEARS = ['2013', '2014', '2015', '2016']

SOLAR_IRRADIANCE_DIR = os.path.abspath(os.path.join(SOURCE_FILES_DIR, 'solar_irradiance'))
WIND_SPEED_DIR = os.path.abspath(os.path.join(SOURCE_FILES_DIR, 'wind_speed'))



def read_json(f):
	with open(f) as fin:
		return json.load(fin)

def test_echo():
	with requests.get(ECHO_URL + 'automated_testing') as r:
		assert r.ok
		assert r.text == 'Echo: automated_testing'

def test_test_url():
	with requests.get(TEST_URL) as r:
		assert r.ok


def _run_estimate(data):
	with requests.post(ESTIMATE_URL, json=data) as r:
		assert r.ok
		task = r.text.split(' ')[-1].rstrip()

	response_received = False
	i = 0
	while not (response_received or (i > 240)):
		i = i + 1
		with requests.get(TASK_STATUS_URL + task) as rr:
			assert rr.ok
			d = json.loads(rr.text)

		if d['status'].startswith('complete'):
			status, value_str, model_name = d['status'].split('|')
			response_received = True
		elif d['status'] == 'running model':
			sleep(1)
			continue
		else:
			raise Exception

	assert response_received
	gen = float(value_str) * (float(data['capacity_mw']) / 1000. * 24 * 365)
	return gen

def test_estimate(input_file):
	data = read_json(input_file)
	expected_gen = data.pop('expected_generation')
	gen = _run_estimate(data)
	assert abs(gen - expected_gen) < 0.01

def test_baseline():
	data = {
		'country': 'Ethiopia',
		'estimating_year': '2016',
		'fuel_type': 'Hydro'
	}
	expected_capacity_factor = 0.51
	with requests.post(BASELINE_URL, json=data) as r:
		assert r.ok
	cf_result = r.text.rstrip()
	if cf_result in ['nan', 'None']:
		capacity_factor = None
	else:
		capacity_factor = float(cf_result)
	assert abs(capacity_factor - expected_capacity_factor) < 0.01

def test_data_resources():
	assert os.path.exists(MODEL_DIR)
	assert os.path.exists(SOURCE_FILES_DIR)
	assert os.path.exists(HYDRO_BASINS_DIR)
	assert os.path.exists(HYDRO_RUNOFF_DIR)
	assert os.path.exists(SOLAR_IRRADIANCE_DIR)
	assert os.path.exists(WIND_SPEED_DIR)

	for continent in HYDRO_BASINS_CONTINENTS:
		p = os.path.join(HYDRO_BASINS_DIR, HYDRO_BASINS_CONTINENT_FMT.format(continent))
		assert os.path.isdir(p)

	for year in HYDRO_RUNOFF_YEARS:
		p = os.path.join(HYDRO_RUNOFF_DIR, HYDRO_RUNOFF_FMT.format(year))
		assert os.path.isfile(p)





test_data_resources()
test_echo()
test_test_url()
test_estimate(os.path.join(TEST_DIR, 'example-solar-with-age.json'))
test_estimate(os.path.join(TEST_DIR, 'example-solar-without-age.json'))
test_estimate(os.path.join(TEST_DIR, 'example-wind.json'))
test_estimate(os.path.join(TEST_DIR, 'example-hydro.json'))
test_estimate(os.path.join(TEST_DIR, 'example-gas.json'))
test_baseline()





print('tests successful')
