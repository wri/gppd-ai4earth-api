from gppd_ai4earth import load_files

COUNTRY_NAME_THESAURUS = load_files.make_country_names_thesaurus()
FUEL_TYPE_THESAURUS = load_files.make_fuel_type_thesaurus()



def name_projection(source_format, country, target_format):
  	return COUNTRY_NAME_THESAURUS.loc[COUNTRY_NAME_THESAURUS[source_format] == country,target_format].values[0]
    
    
    
def fuel_projection(source_format, fuel, target_format):
    return FUEL_TYPE_THESAURUS.loc[FUEL_TYPE_THESAURUS[source_format] == fuel,target_format].values[0]