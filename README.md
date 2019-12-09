# gppd-ai4earth-api

Notes on the generation estimation API.<br/>

API Usage:<br/>
This API is used for estimating plant-level annual generation in the form of annual capacity factor. Capacity factors measure the ratio of actual to maximum potential generation for each plant. (see https://en.wikipedia.org/wiki/Capacity_factor for more details about capacity factor and how it can be converted to generation) on a global scale. The API can provide estimates for both actual and virtual power stations as long as the sets of parameters are provided correctly for each of the fuel specific model.<br/>

API Coverage:<br/>
This API covers generation estimates for power facilities in four catogories: wind-powered, solar-powered, hydroelectricity-powered, and gas-fired.<br/>
The current API covers different range of years for different models, here's the range list for each of them:<br/>
Wind: 2000 - 2018<br/>
Solar: 2000 - 2018<br/>
Hydro: 2013 - 2017<br/>
Gas: 2014 - 2017<br/>

API Parameters:<br/>
Required parameters depend on the category. Here are lists of parameters needed for each model:<br/>
Wind: fuel_type, capacity_mw, estimating_year, commissioning_year, country, lat, lon<br/>
Solar: fuel_type, capacity_mw, estimating_year, commissioning_year, country, lat, lon<br/>
Hydro: fuel_type, capacity_mw, estimating_year, country, lat, lon<br/>
Gas: fuel_type, capacity_mw, estimating_year, commissioning_year, turbine_type, country, lat, lon<br/>


Parameters:<br/>
fuel_type: The category of the power plant. Should be one of ['Wind','Solar','Hydro','Gas']<br/>
capacity_mw: The capacity of the power plant in MegaWatt. A numerical value (can be integer or decimal)<br/>
estimating_year: The year of interest for estimation. A integer value.<br/>
commissiong_year: The commissioning year of the power plant. A integer value.<br/>
country: The country where the power plant located. Country naming convention should be consistent with the Global Power Plant Database (can be accessed through http://datasets.wri.org/dataset/globalpowerplantdatabase)<br/>
lat: The latitude of the power plant. A numerical value (can be integer or decimal)<br/>
lon: The longitude of the power plant. A numerical value (can be integer or decimal)<br/>
turbine_type: The type of gas turbines used by the power plant. Should be one of ['CCGT', 'CS', 'FC', 'GT', 'IC', 'ST'] (Definition for each of the turbine types can be found in our methodology documentation as listed in this readme file)<br/>

Relevant Links:<br/>
Methodology documentation (WIP) - https://docs.google.com/document/d/1XqkXGpUraoxI6eJdmrlsE_2FMX3XEFBBaJIWWiEb5QI/edit?usp=sharing<br/>