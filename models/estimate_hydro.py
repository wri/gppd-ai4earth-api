import csv
import requests
import json
from time import sleep

#OVERRIDE_SKIP_COUNT = 10131 # WRI1002350, line 5462
#OVERRIDE_SKIP_COUNT = 17924 # WRI1003087, line 8247
#OVERRIDE_SKIP_COUNT = 21002 # WRI1030415, line 9894
#OVERRIDE_SKIP_COUNT = 13350
#OVERRIDE_SKIP_COUNT = 31548
OVERRIDE_SKIP_COUNT = 0


GPPD_PATH = 'global_power_plant_database.csv'

API_POST_JOB_URL = 'http://localhost:5151/v1/my_api/tasker/estimate'
API_FETCH_RESULT_URL = 'http://localhost:5151/v1/my_api/tasker/task/'

OUTPUT_CSV_FILE = 'output/hydro_estimates.csv'
OUTPUT_FIELDS = ['gppd_idnr', 'year', 'reported_generation', 'estimated_generation', 'model_name'] 


# Load the global power plant database
gppd = list(csv.DictReader(open(GPPD_PATH)))
print(len(gppd), 'plants')


def run_estimate(data):
    with requests.post(API_POST_JOB_URL, json=data) as r:
        assert r.ok
        print(r.text)
        task = r.text.split(' ')[-1]

    response_received = False
    i = 0 
    while not (response_received or i > 120):
        i = i + 1
        with requests.get(API_FETCH_RESULT_URL + task.rstrip()) as rr:
            assert rr.ok
            d = json.loads(rr.text)

        if d['status'].startswith('complete'):
            status, value_str, model_name = d['status'].split('|')
            response_received = True
        elif d['status'] == 'running model':
            sleep(0.1)
            continue
        elif d['status'].startswith('Task failed'):
            break

    assert response_received
    if data['estimating_year'] % 4:
        num_days_in_year = 365
    else:
        num_days_in_year = 366
    gen = float(value_str) * (float(data['capacity_mw']) / 1000. * 24 * num_days_in_year)
    return gen, model_name


def transform_hydro_row(row, est_year):
    param_name_map = {
        'primary_fuel': ('fuel_type', str),
        'capacity_mw': ('capacity_mw', float),
        'country_long': ('country', str),
        'latitude': ('lat', float),
        'longitude': ('lon', float),
    }
    outd = {}
    for k, transform in param_name_map.items():
        col, func = transform
        try:
            outd[col] = func(row[k])
        except:
            pass

    outd['estimating_year'] = int(est_year)
    return outd


with open(OUTPUT_CSV_FILE, 'a', newline='') as fout:
	writer = csv.DictWriter(fout, fieldnames=OUTPUT_FIELDS)
	if OVERRIDE_SKIP_COUNT == 0:
		writer.writeheader()
		pass

	for i, pp in enumerate(gppd):
		if i < OVERRIDE_SKIP_COUNT:
			continue
		if pp['primary_fuel'] != 'Hydro':
			continue
		print('plant #', i)
		for year in range(2013, 2018):
			row = transform_hydro_row(pp, year)
			if row['country'] == 'United States of America':
				continue
			try:
				gwh, model_name = run_estimate(row)
			except:
				continue
			else:
				outd = {
					'gppd_idnr': pp['gppd_idnr'],
					'year': year,
					'reported_generation': pp[f'generation_gwh_{year}'],
					'estimated_generation': gwh,
					'model_name': model_name
				}
				writer.writerow(outd)
				fout.flush()

