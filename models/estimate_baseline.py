import csv
import requests
import json
from time import sleep

API_POST_JOB_URL = 'http://localhost:5151/v1/my_api/tasker/baseline'

GPPD_PATH = 'global_power_plant_database.csv'
OUTPUT_CSV_FILE = 'output/baseline_estimates.csv'
OUTPUT_FIELDS = ['country', 'fuel', 'year', 'capacity_factor']


gppd = list(csv.DictReader(open(GPPD_PATH)))
print(len(gppd), 'plants')


def run_estimate(data):
    with requests.post(API_POST_JOB_URL, json=data) as r:
        assert r.ok
        print(r.text)
    return r.text

countries = sorted(list(set([(pp['country'], pp['country_long']) for pp in gppd ])), key=lambda x: x[0])
fuels = sorted(list(set([pp['primary_fuel'] for pp in gppd ])))

with open(OUTPUT_CSV_FILE, 'w', newline='') as fout:
	writer = csv.DictWriter(fout, fieldnames=OUTPUT_FIELDS)
	writer.writeheader()

	for iso, country in countries:
		for fuel in fuels:
			for yr in range(2014, 2018):
				data = {
					'country': country,
					'estimating_year': yr,
					'fuel_type': fuel
				}
				cf = run_estimate(data)
				print(iso, fuel, yr, cf)

				outd = {
					'country': iso,
					'fuel': fuel,
					'year': yr,
					'capacity_factor': cf if cf not in ['None', 'nan'] else ''
				}

				writer.writerow(outd)
				fout.flush()

