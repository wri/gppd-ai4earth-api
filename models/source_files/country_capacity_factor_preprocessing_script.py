# from gppd_ai4earth import load_files
# from gppd_ai4earth import thesaurus_projection
import numpy as np
import pandas as pd
import json

COMBUSTION_CF_YEAR_RANGE = [str(y) for y in range(2014,2018)]
COMBUSTION_FUEL_TYEPS = ['Coal','Oil','Gas']

TOTAL_GEN_PATH = "gen_by_year_country_fuel.json"
with open(TOTAL_GEN_PATH,"r") as file:
	TOTAL_GEN = json.load(file)

TOTAL_CAP_PATH = "PLATTS MARCH 2017.csv"
TOTAL_CAP = pd.read_csv(TOTAL_CAP_PATH,encoding='ISO-8859-1')

COUNTRY_NAME_THESAURUS = pd.read_csv("country_information_updated_v4.csv",encoding='utf-8')
FUEL_TYPE_THESAURUS = pd.read_csv("fuel_thesaurus.csv")


def name_projection(source_format, country, target_format):
	return COUNTRY_NAME_THESAURUS.loc[COUNTRY_NAME_THESAURUS[source_format] == country,target_format].values[0]

	
def fuel_projection(source_format, fuel, target_format):
	return FUEL_TYPE_THESAURUS.loc[FUEL_TYPE_THESAURUS[source_format] == fuel,target_format].values[0]


def get_total_generation(year, country, fuel):
	try:
		return TOTAL_GEN[year][country][fuel]
	except:
		return np.NaN


def country_fuel_platts_projection(country, fuel):
	platts_country_name = name_projection('primary_country_name', country, 'platts_country_name')
	platts_fuel_type = fuel_projection('primary_fuel_type', fuel, 'PLATTS_fuel_type')
	return platts_country_name, platts_fuel_type


def get_total_capacity_platts(country, fuel):
	if not isinstance(country, str):
		return np.NaN

	country_parts = country.split(';')
	total_cap = -1

	for cp in country_parts:
		cp_total_cap = platts_query_capacity(cp, fuel)

		if np.isnan(cp_total_cap):
			continue
		total_cap += cp_total_cap
	
	if total_cap == -1:
		return np.NaN
	return total_cap + 1



def platts_query_capacity(country, fuel):
	records = TOTAL_CAP.loc[(TOTAL_CAP['COUNTRY'] == country) & 
									 (TOTAL_CAP['FUEL'] == fuel) & 
									 (TOTAL_CAP['STATUS'] == 'OPR')]
	if len(records) > 0:
		return records['MW'].sum()
	return np.NaN


def num_days_of_year(year):
		return 366 if int(year) % 4 == 0 else 365


if __name__ == '__main__':
	country_list = set(list(COUNTRY_NAME_THESAURUS['primary_country_name']))

	cf = {}

	for year in COMBUSTION_CF_YEAR_RANGE:
		if year not in cf:
			cf[year] = {}
		print(year)
		for country in country_list:
			if country not in cf[year]:
				cf[year][country] = {}

			for fuel in COMBUSTION_FUEL_TYEPS:
				
				total_gen = get_total_generation(year, country, fuel)
				platts_country, platts_fuel = country_fuel_platts_projection(country, fuel)
				total_cap = get_total_capacity_platts(platts_country, platts_fuel)
				days_of_year = num_days_of_year(year)

				if total_cap == 0 or np.isnan(total_cap) or np.isnan(total_gen):
					capacity_factor = np.NaN
				else:
					capacity_factor = total_gen / (total_cap * 24 * days_of_year / 1000)

				cf[year][country][fuel] = capacity_factor

	with open('preprocessed_capacity_factors.json','w') as file:
		json.dump(cf, file)


