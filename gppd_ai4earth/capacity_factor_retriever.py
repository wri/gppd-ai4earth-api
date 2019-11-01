from gppd_ai4earth import load_files
from gppd_ai4earth import thesaurus_projection
import numpy as np

COMBUSTION_CF_YEAR_RANGE = [str(y) for y in range(2014,2018)]
RENEWABLE_CF_YEAR_RANGE = [str(y) for y in range(2000,2019)]
COMBUSTION_FUEL_TYEPS = ['Coal','Oil','Gas']
RENEWABLE_FUEL_TYEPS = ['Hydro','Wind','Solar']

class AvgCapacityFactorRetriever:
    
    
    
    def __init__(self):
        
        self.combustion_cf_lookup_dict = load_files.load_combustion_cf()
        # self.total_cap_oecd = load_files.load_total_cap_oecd()
        # self.total_cap_platts = load_files.load_total_cap_platts()
        self.renewable_cf_lookup_dict = {'Wind': load_files.load_wind_cf(),
                                         'Solar': load_files.load_solar_cf(),
                                         'Hydro': load_files.load_hydro_cf()}
        # self.country_name_thesaurus = load_files.make_country_names_thesaurus()
        # self.fuel_type_thesaurus = load_files.make_fuel_type_thesaurus()
        self.valid_country_names = set(thesaurus_projection.COUNTRY_NAME_THESAURUS['primary_country_name'])
    
    
    
    def retrieve_capacity_factor(self, year, country, fuel):
        
        self.check_country_name(country)
        
        year = str(year)
        
        if fuel in COMBUSTION_FUEL_TYEPS:
            self.check_year_availability(year, COMBUSTION_CF_YEAR_RANGE, 'combustion power plants')
            return self.combustion_capacity_factor(year, country, fuel)
        
        elif fuel in RENEWABLE_FUEL_TYEPS:
            self.check_year_availability(year, RENEWABLE_CF_YEAR_RANGE, 'renewable power plants')
            return self.renewable_capacity_factor(year, country, fuel)
        
        else: 
            valid_fuel_types = ', '.join(COMBUSTION_FUEL_TYEPS + RENEWABLE_FUEL_TYEPS)
            fuel_type_error_message = '{} not found. Please use one of {}'.format(fuel, valid_fuel_types)
            raise ValueError(fuel_type_error_message)
    
    

    def combustion_capacity_factor(self, year, country, fuel):
        days_of_year = self.num_days_of_year(year)
        
        # numerator = self.get_total_gen(year, country, fuel)
        # if country == 'United Kingdom':
        #     denominator = self.get_total_cap_oecd(year, country, fuel)
        # else:
        #     denominator = self.get_total_cap_platts(country, fuel)
        country_cf = self.combustion_cf_lookup_dict[year][country][fuel]
        
        return country_cf



    def renewable_capacity_factor(self, year, country, fuel):
        year = int(year)
        days_of_year = self.num_days_of_year(year)
        cf_lookup_table = self.renewable_cf_lookup_dict[fuel]
        irena_country_name = thesaurus_projection.name_projection('primary_country_name', country, 'irena_country_name')

        numerator = cf_lookup_table.loc[(cf_lookup_table['Country/area'] == irena_country_name) & 
                                        (cf_lookup_table['Indicator'] == 'Electricity generation (GWh)'), str(year)].values[0]

        denominator = cf_lookup_table.loc[(cf_lookup_table['Country/area'] == irena_country_name) & 
                                          (cf_lookup_table['Indicator'] == 'Electricity capacity (MW)'), str(year)].values[0]

        if (self.isNan(numerator) or self.isNan(denominator) or denominator == 0):
            return np.NaN
        capacity_factor = numerator / (denominator * 24 * days_of_year / 1000)
        return capacity_factor




    def check_country_name(self, country):
        country_not_available_message = '{} not found. Valid country names {}'.format(country, self.valid_country_names)
        assert country in self.valid_country_names, country_not_available_message



    def check_year_availability(self, year, year_list, plant_category):
        joined_year_list = ', '.join(year_list)
        year_not_available_message = 'Years beyond {} are not available for {}'.format(joined_year_list, plant_category)
        assert year in year_list, year_not_available_message

    

    def num_days_of_year(self, year):
        return 366 if int(year) % 4 == 0 else 365
    


    # def get_total_gen(self, year, country, fuel):
    #     return self.total_gen[year][country][fuel]


    
    def isNan(self, value):
        return False if value == value else True
    
    
    
    # def get_total_cap_oecd(self, year, country, fuel):
    #     oecd_country_name = thesaurus_projection.name_projection('primary_country_name', country, 'oecd_library_country_name')
    #     if self.isNan(oecd_country_name):
    #         return -1
        
    #     oecd_fuel_type = thesaurus_projection.fuel_projection('primary_fuel_type', fuel, 'OECD_fuel_type')
    #     total_cap = self.total_cap_oecd.loc[(self.total_cap_oecd['COUNTRY'] == oecd_country_name) & 
    #                                         (self.total_cap_oecd['PRODUCT'] == oecd_fuel_type), year].values[0]
    #     if total_cap in ['..','0']:
    #         return -1
        
    #     return int(total_cap)
    
    
    
    def name_projection(self, source_farmat, country, target_format):
        return self.country_name_thesaurus.loc[self.country_name_thesaurus[source_format] == country,target_format].values[0]
    
    
    
    def fuel_projection(self, source_format, fuel, target_format):
        return self.fuel_type_thesaurus.loc[self.fuel_type_thesaurus[fource_format] == fuel,target_format].values[0]
    
    
    
    # def get_total_cap_platts(self, country, fuel):
    #     platts_country_name = thesaurus_projection.name_projection('primary_country_name', country, 'platts_country_name')
    #     platts_fuel_type = thesaurus_projection.fuel_projection('primary_fuel_type', fuel, 'PLATTS_fuel_type')
    #     total_cap = self.total_cap_platts.loc[(self.total_cap_platts['COUNTRY'] == platts_country_name) & 
    #                                      (self.total_cap_platts['FUEL'] == platts_fuel_type) & 
    #                                      (self.total_cap_platts['STATUS'] == 'OPR'),'MW'].sum()
    #     return total_cap