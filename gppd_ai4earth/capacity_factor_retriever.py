from gppd_ai4earth import load_files
from gppd_ai4earth import thesaurus_projection
import numpy as np

COMBUSTION_CF_YEAR_RANGE = [str(y) for y in range(2014,2018)]
RENEWABLE_CF_YEAR_RANGE = [str(y) for y in range(2000,2019)]
COMBUSTION_FUEL_TYEPS = ['Coal','Oil','Gas', 'Nuclear', 'Biomass', 'Waste', 'Geothermal', 'Tide', 'Other']
RENEWABLE_FUEL_TYEPS = ['Hydro','Wind','Solar']

class AvgCapacityFactorRetriever:
    
    '''
    This class retrieve capacity factor given country, year and fuel type
    '''
    
    def __init__(self):
        
        self.combustion_cf_lookup_dict = load_files.load_combustion_cf()
        self.renewable_cf_lookup_dict = {'Wind': load_files.load_wind_cf(),
                                         'Solar': load_files.load_solar_cf(),
                                         'Hydro': load_files.load_hydro_cf()}
        self.valid_country_names = set(thesaurus_projection.COUNTRY_NAME_THESAURUS['primary_country_name'])
    
    
    
    def retrieve_capacity_factor(self, year, country, fuel):
        '''
        This function retrieves capacity factor according to the fuel type
        '''
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
        '''
        This function returns capacity factors of combustion power plants based on year, country and fuel type
        '''
        days_of_year = self.num_days_of_year(year)
        country_cf = self.combustion_cf_lookup_dict[year][country][fuel]
        
        return country_cf



    def renewable_capacity_factor(self, year, country, fuel):
        '''
        This function returns capacity factors of renewables power plants based on year, country and fuel type
        '''
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
        '''
        This function checks the country name and makes sure the given country name is consistent 
        with the naming convention in the Global Power Plant Database
        '''
        country_not_available_message = '{} not found. Valid country names {}'.format(country, self.valid_country_names)
        assert country in self.valid_country_names, country_not_available_message



    def check_year_availability(self, year, year_list, plant_category):
        '''
        This function checks the year of estimation and ensures it does not exceeds the year range of estimation
        '''
        joined_year_list = ', '.join(year_list)
        year_not_available_message = 'Years beyond {} are not available for {}'.format(joined_year_list, plant_category)
        assert year in year_list, year_not_available_message

    

    def num_days_of_year(self, year):
        return 366 if int(year) % 4 == 0 else 365
    

    
    def isNan(self, value):
        return False if value == value else True
    
    
    
    def name_projection(self, source_farmat, country, target_format):
        return self.country_name_thesaurus.loc[self.country_name_thesaurus[source_format] == country,target_format].values[0]
    
    
    
    def fuel_projection(self, source_format, fuel, target_format):
        return self.fuel_type_thesaurus.loc[self.fuel_type_thesaurus[source_format] == fuel,target_format].values[0]
