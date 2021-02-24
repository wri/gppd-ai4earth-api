# gppd-ai4earth-api

## Usage, first time, needing to build docker image

```
# (optional) setup python environment
# virtualenv --python=python3.7 venv
# . venv/bin/activate && pip install -r requirements

# obtain HydroBasins dataset
make models/source_files/HydroBasins


# obtain hydro runoff
#  (edit Makefile with your CDS key first)
make models/source_files/hydro_runoff

# ensure docker server is running
sudo systemctl start docker

# build the docker image
docker build .

# label image
docker image tag <image_id> ai4e_13:latest

```


## Usage, for Global Power Plant Database

```
# obtain fresh copy of GPPD
make models/global_power_plant_database.csv

# ensure docker server is running
sudo systemctl start docker

# start docker API container
./dockerup.sh

# run tests
make test

# (optional) perform estimates - go to the models folder
cd models

# estimate baseline
python estimate_baseline.py

# estimate hydro
python estimate_hydro.py

# estimate solar
python estimate_solar.py

# estimate wind
python estimate_wind.py

# merge estimates into GPPD
python make_gppd.py


# ... later to stop the API container
./dockerdown.sh


```



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

Methodology is available in this document: [Estimating Power Plant Generation in the Global Power Plant Database (2020)](https://www.wri.org/publication/estimating-power-plant-generation-global-power-plant-database)

