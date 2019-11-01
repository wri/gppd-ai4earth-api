import pandas as pd

RENEWABLE_CF_LIST = ['Solar_Capacity_Factor_Lookup_Table.xlsx',
					 'Wind_Capacity_Factor_Lookup_Table.xlsx',
					 'Hydro_Capacity_Factor_Lookup_Table.xlsx']


if __name__ == "__main__":

	for renewable_cf in RENEWABLE_CF_LIST:
		temp = pd.read_excel(renewable_cf)
		temp['Country/area'].ffill(inplace = True)
		temp['Technology'].ffill(inplace = True)
		temp.to_csv(renewable_cf.split('.')[0] + '.csv', index = False)