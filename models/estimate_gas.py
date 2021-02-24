import csv
import requests
import json
import pandas as pd
from time import sleep

# where did the processing fail last?
OVERRIDE_SKIP_COUNT = 0

GPPD_PATH = 'global_power_plant_database.csv'
PLATTS_PATH = 'PLATTS MARCH 2017.csv'

API_POST_JOB_URL = 'http://localhost:5151/v1/my_api/tasker/estimate'
API_FETCH_RESULT_URL = 'http://localhost:5151/v1/my_api/tasker/task/'

OUTPUT_CSV_FILE = 'output/gas_estimates.csv'
OUTPUT_FIELDS = ['gppd_idnr', 'year', 'reported_generation', 'estimated_generation', 'model_name'] 


# Load the global power plant database
gppd = pd.read_csv(GPPD_PATH)
gppd = gppd[gppd['primary_fuel'] == 'Gas']
print(len(gppd), 'plants')


# Loading Platts data
platts = pd.read_csv(PLATTS_PATH, encoding='ISO-8859-1')
platts = platts[(platts['STATUS']=='OPR')]
platts_gas_related_ids = platts.loc[platts['FUEL']=='GAS', 'LOCATIONID'].unique()
platts_gas_related = platts[platts['LOCATIONID'].isin(platts_gas_related_ids)]

# Extract Gas dominated plants from all plants
platts_gas_related['FUEL'].replace({'WSTH':'GAS'},inplace = True)

temp = platts_gas_related.groupby(['LOCATIONID','FUEL']).agg({'MW':'sum'})
platts_gas_fuel_proportion = temp.groupby(level = 0).apply(lambda x:x/float(x.sum()))
platts_gas_fuel_proportion.reset_index(inplace=True)

platts_pure_gas_ids = platts_gas_fuel_proportion.loc[platts_gas_fuel_proportion['MW'] >= 0.95,'LOCATIONID']
platts_pure_gas = platts[platts['LOCATIONID'].isin(platts_pure_gas_ids)]

# Extract gas plants operated under a single generating technology
platts_pure_gas['UTYPE_ORIGIN'] = platts_pure_gas['UTYPE']
platts_pure_gas['UTYPE'] = platts_pure_gas['UTYPE'].replace({'GT/C':'CCGT',
                                                             'ST/C':'CCGT',
                                                             'GT/CP':'CCGT',
                                                             'ST/CP':'CCGT',
                                                             'IC/H':'IC',
                                                             'IC/CD':'IC',
                                                             'CCSS':'CS',
                                                             'CCSS/P':'CS',
                                                             'GT/S':'GT',
                                                             'ST/S':'ST',
                                                             'GT/H':'GT',
                                                             'ST/D':'ST',
                                                             'GT/D':'GT'})
temp = platts_pure_gas.groupby(['LOCATIONID','UTYPE']).agg({'MW':'sum'})
platts_gas_utype_proportion = temp.groupby(level = 0).apply(lambda x:x/float(x.sum()))
platts_gas_utype_proportion.reset_index(inplace=True)
platts_id2utype_df = platts_gas_utype_proportion.loc[platts_gas_utype_proportion['MW'] >= 0.95,['LOCATIONID','UTYPE']]
platts_id2utype = platts_id2utype_df.set_index('LOCATIONID').to_dict()['UTYPE']

# impute unit type values for GPPD
platts_id2utype_df['LOCATIONID'] = platts_id2utype_df['LOCATIONID'].apply(str)
gppd_with_utype = pd.merge(gppd,platts_id2utype_df,'left',left_on='wepp_id',right_on='LOCATIONID')

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


def transform_gas_row(row, est_year):
    param_name_map = {
        'primary_fuel': ('fuel_type', str),
        'capacity_mw': ('capacity_mw', float),
        'commissioning_year': ('commissioning_year', float),
        'country_long': ('country', str),
		'UTYPE': ('turbine_type', str)
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


with open(OUTPUT_CSV_FILE, 'a') as fout:
	writer = csv.DictWriter(fout, fieldnames=OUTPUT_FIELDS)
	if OVERRIDE_SKIP_COUNT == 0:
		writer.writeheader()

	for i, pp in gppd_with_utype.iterrows():
		if i < OVERRIDE_SKIP_COUNT:
			continue
		print('plant #', i)
		for year in range(2014, 2019):
			try:
				gwh, model_name = run_estimate(transform_gas_row(pp, year))
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

