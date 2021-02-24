"""Transform ERA precipitation data into monthly averages."""

if __name__ == '__main__':
	from netCDF4 import Dataset
	import numpy as np
	import os
	import sys


	RAW_DATA_PATH = sys.argv[1] # os.path.join(SOURCE_PATH,'hydro_runoff')
	YEARS = [int(y) for y in os.listdir(RAW_DATA_PATH) if not y.startswith('.')]

	for year in YEARS:
		original = Dataset(os.path.join(RAW_DATA_PATH, '{0}/{0}_monthly_avg.nc'.format(year)))
		updated_file_path = os.path.join(RAW_DATA_PATH, str(year), str(year) + '_monthly_avg_transformed.nc')
		new = Dataset(updated_file_path, 'w')

		new.createDimension('lon', 1440)
		new.createDimension('lat', 721)
		new.createDimension('time', 12)

		new.createVariable('lon', np.float64, ('lon',))
		new.createVariable('lat', np.float64, ('lat',))
		new.createVariable('time', np.float64, ('time',))

		new.variables['lat'].setncattr('standard_name', 'latitude')
		new.variables['lat'].setncattr('long_name', 'latitude')
		new.variables['lat'].setncattr('units', 'degrees_north')
		new.variables['lat'].setncattr('axis', 'Y')
		new.variables['lat'][:] = np.arange(-90, 90.25, 0.25)

		new.variables['lon'].setncattr('standard_name', 'longitude')
		new.variables['lon'].setncattr('long_name', 'longitude')
		new.variables['lon'].setncattr('units', 'degrees_east')
		new.variables['lon'].setncattr('axis', 'X')
		new.variables['lon'][:] = np.arange(-180, 180, 0.25)

		new.variables['time'].setncattr('standard_name', 'time')
		new.variables['time'].setncattr('long_name', 'time')
		new.variables['time'].setncattr('units', 'hours since 1900-01-01 00:00:00.0')
		new.variables['time'].setncattr('calendar', 'gregorian')
		new.variables['time'][:] = np.array(original.variables['time'][:])

		for var in ['sro', 'ssro']:
			print(var)
			new.createVariable(var, np.float64, ('time', 'lat', 'lon'))
			new.variables[var].setncattr('standard_name', original.variables[var].long_name)
			new.variables[var].setncattr('long_name', original.variables[var].long_name)
			new.variables[var].setncattr('units', original.variables[var].units)
			arr = np.array(original.variables[var][:])
			new_arr = np.flip(np.concatenate((arr[:, :, 720:], arr[:, :, :720]), axis=2), axis=1)
			new.variables[var][:] = new_arr

		new.close()
	sys.exit(0)
