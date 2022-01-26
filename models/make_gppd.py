import csv

gppd = list(csv.DictReader(open('global_power_plant_database.csv')))

hydro_r = csv.DictReader(open('output/hydro_estimates.csv'))
solar_r= csv.DictReader(open('output/solar_estimates.csv'))
wind_r = csv.DictReader(open('output/wind_estimates.csv'))
baseline_r = csv.DictReader(open('output/baseline_estimates.csv'))

generation = {}
for hp in hydro_r:
	hpid = hp['gppd_idnr']
	vals = generation.get(hpid, {})
	vals[hp['year']] = (hp['estimated_generation'], hp['model_name'])
	generation[hpid] = vals

for sp in solar_r:
	spid = sp['gppd_idnr']
	vals = generation.get(spid, {})
	vals[sp['year']] = (sp['estimated_generation'], sp['model_name'])
	generation[spid] = vals

for wp in wind_r:
	wpid = wp['gppd_idnr']
	vals = generation.get(wpid, {})
	vals[wp['year']] = (wp['estimated_generation'], wp['model_name'])
	generation[wpid] = vals


model_name_map = {
	'ai4e_solar_model_no_age': 'SOLAR-V1-NO-AGE',
	'ai4e_solar_model': 'SOLAR-V1',
	'ai4e_hydro_model': 'HYDRO-V1',
	'ai4e_wind_model': 'WIND-V1',
}

baseline_data = {}
# iso, year, fuel
for bs in baseline_r:
	c = bs['country']
	yr = bs['year']
	f = bs['fuel']
	cc = baseline_data.get(c, {})
	yy = cc.get(yr, {})
	yy[f] = bs['capacity_factor']
	cc[yr] = yy
	baseline_data[c] = cc



new_gppd = []
for pp in gppd:
	ppid = pp['gppd_idnr']
	c = pp['country']
	f = pp['primary_fuel']

	for yr in range(2013,2018):
		existing = f'generation_gwh_{yr}'
		if '.' in pp[existing]:
			pp[f] = pp[existing][:pp[existing].index('.') + 3]

		val = ''
		model = 'NO-ESTIMATION'
		pp[f'estimated_generation_gwh_{yr}'] = val
		pp[f'estimated_generation_note_{yr}'] = model

		if f == 'Biomass':
			continue

		if ppid in generation:
			if str(yr) in generation[ppid]:
				val, model = generation[ppid][str(yr)]
				val = val[:val.index('.') + 3]
				pp[f'estimated_generation_gwh_{yr}'] = val
				pp[f'estimated_generation_note_{yr}'] = model_name_map[model]

		if ((yr == 2017) and (ppid in generation) and (pp[f'estimated_generation_note_{yr}'] == 'NO-ESTIMATION')) or ((yr == 2017) and (ppid not in generation)):
			days_in_yr = 365 if yr % 4 else 366
			try:
				bs = baseline_data[c][str(yr)][f]
			except:
				print('NO BASELINE', c, yr, f)
				bs = None
			if bs:
				val = str(float(pp['capacity_mw']) * float(bs) * days_in_yr * 24 / 1000)
				val = val[:val.index('.') + 3]
				model = 'CAPACITY-FACTOR-V1'
			else:
				val = ''
				model = 'NO-ESTIMATION'
			pp[f'estimated_generation_gwh_{yr}'] = val
			pp[f'estimated_generation_note_{yr}'] = model

	new_gppd.append(pp)

OUTPUT_CSV_FILE = 'global_power_plant_database_merged_final.csv'
OUTPUT_FIELDS = [
	'country',
	'country_long',
	'name',
	'gppd_idnr',
	'capacity_mw',
	'latitude',
	'longitude',
	'primary_fuel',
	'other_fuel1',
	'other_fuel2',
	'other_fuel3',
	'commissioning_year',
	'owner',
	'source',
	'url',
	'geolocation_source',
	'wepp_id',
	'year_of_capacity_data',
	'generation_gwh_2013',
	'generation_gwh_2014',
	'generation_gwh_2015',
	'generation_gwh_2016',
	'generation_gwh_2017',
	'generation_gwh_2018',
	'generation_gwh_2019',
	'generation_data_source',
	'estimated_generation_gwh_2013',
	'estimated_generation_gwh_2014',
	'estimated_generation_gwh_2015',
	'estimated_generation_gwh_2016',
	'estimated_generation_gwh_2017',
	'estimated_generation_note_2013',
	'estimated_generation_note_2014',
	'estimated_generation_note_2015',
	'estimated_generation_note_2016',
	'estimated_generation_note_2017']

with open(OUTPUT_CSV_FILE, 'w') as fout:
	w = csv.DictWriter(fout, fieldnames=OUTPUT_FIELDS, extrasaction='ignore')
	w.writeheader()
	w.writerows(new_gppd)


