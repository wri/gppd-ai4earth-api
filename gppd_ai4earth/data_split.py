from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

def split(df, y_col, test_precent = 0.2, validation_percent = 0.2 , X_cols = None, random_state = 0):
	size = df.shape[0]
	test_size = int(np.round(size * test_precent))
	val_size = int(np.round(size * validation_percent))

	data = df.copy()
	y_data = df[y_col]

	if X_cols is not None:
		X_data = data[X_cols]
	else:
		X_data = X_data.drop([y_col], axis=1)

	X_model, X_test, y_model, y_test = train_test_split(X_data, y_data, test_size = test_size, random_state = random_state)
	X_train, X_val, y_train, y_val = train_test_split(X_model, y_model, test_size = val_size, random_state = random_state)

	return ((X_train,y_train),(X_val, y_val),(X_test, y_test))

