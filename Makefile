HYDROBASINS_LOCAL_DIR := models/source_files/HydroBasins
CDS_KEY := ADD_YOUR_KEY_HERE


# no arguments = test
.PHONY: default
default: test

# tests
.PHONY: test
test:
	python tests/tests.py

# fetch most recent GPPD
.PHONY: models/global_power_plant_database.csv
models/global_power_plant_database.csv:
	wget -O models/global_power_plant_database.csv https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv

# fetch all HydroBASINS shapefiles
.PHONY: models/source_files/HydroBasins
models/source_files/HydroBasins: hydrobasins_af hydrobasins_ar hydrobasins_as hydrobasins_au hydrobasins_eu hydrobasins_gr hydrobasins_na hydrobasins_sa hydrobasins_si


# HydroBASINS Africa
.PHONY: hydrobasins_af
hydrobasins_af:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -nv -O $(HYDROBASINS_LOCAL_DIR)/hybas_af_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABSBGFylsZ9KoG8zYRvOTzqa/HydroBASINS/standard/af/hybas_af_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_af_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_af_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_af_lev12_v1c.zip


# HydroBASINS Arctic
.PHONY: hydrobasins_ar
hydrobasins_ar:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -nv -O $(HYDROBASINS_LOCAL_DIR)/hybas_ar_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADaA0icxaPYgaQGuLbSaKfna/HydroBASINS/standard/ar/hybas_ar_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_ar_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_ar_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_ar_lev12_v1c.zip


# HydroBASINS Asia
.PHONY: hydrobasins_as
hydrobasins_as:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_as_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADWZKiGaCncO5JdRLmkIduMa/HydroBASINS/standard/as/hybas_as_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_as_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_as_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_as_lev12_v1c.zip


# HydroBASINS Australia
.PHONY: hydrobasins_au
hydrobasins_au:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_au_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAA5lwuZZ5EZsxrx_EBQGW3ma/HydroBASINS/standard/au/hybas_au_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_au_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_au_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_au_lev12_v1c.zip


# HydroBASINS Europe
.PHONY: hydrobasins_eu
hydrobasins_eu:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_eu_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AADULrBSkGy5dHOZ8vMxWpWxa/HydroBASINS/standard/eu/hybas_eu_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_eu_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_eu_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_eu_lev12_v1c.zip


# HydroBASINS Greenland
.PHONY: hydrobasins_gr
hydrobasins_gr:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_gr_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AACNOTXj-M1T-rpz5k_QJd6Ka/HydroBASINS/standard/gr/hybas_gr_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_gr_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_gr_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_gr_lev12_v1c.zip


# HydroBASINS North America
.PHONY: hydrobasins_na
hydrobasins_na:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_na_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AAA1ofV7PhSY_x7vQluubYyNa/HydroBASINS/standard/na/hybas_na_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_na_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_na_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_na_lev12_v1c.zip


# HydroBASINS South America
.PHONY: hydrobasins_sa
hydrobasins_sa:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_sa_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABPzWxd07pmshjZl6Y0NPXNa/HydroBASINS/standard/sa/hybas_sa_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_sa_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_sa_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_sa_lev12_v1c.zip


# HydroBASINS Siberia
.PHONY: hydrobasins_si
hydrobasins_si:
	mkdir -p $(HYDROBASINS_LOCAL_DIR)
	wget -O $(HYDROBASINS_LOCAL_DIR)/hybas_si_lev12_v1c.zip https://www.dropbox.com/sh/hmpwobbz9qixxpe/AABtI2KbgItfLp4jmHcvZhDea/HydroBASINS/standard/si/hybas_si_lev12_v1c.zip?dl=1
	unzip $(HYDROBASINS_LOCAL_DIR)/hybas_si_lev12_v1c.zip -d $(HYDROBASINS_LOCAL_DIR)/hybas_si_lev12_v1c && rm $(HYDROBASINS_LOCAL_DIR)/hybas_si_lev12_v1c.zip
	

# Hydro Runoff
.PHONY: models/source_files/hydro_runoff
models/source_files/hydro_runoff:
	python models/source_files/hydro_runoff_tool_scripts/download_ERA5_monthly_averages.py $(CDS_KEY) models/source_files/hydro_runoff \
	&& python models/source_files/hydro_runoff_tool_scripts/transform_ERA5_monthly_averages.py models/source_files/hydro_runoff \
	&& rm models/source_files/hydro_runoff/**/*_monthly_avg.nc



