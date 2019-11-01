"""
This file contains functions that will be useful in understanding missing data and imputing using KNN.
"""

import pandas as pd
import numpy as np
import missingno as msno
from fancyimpute import KNN 
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import gppd_co2.dfreader as dfr


def missing_viz(file_path):
    """
    *Drops NAs based on co2_emissions_tonne column
    
    *Provides the sum of missing values per column.
    
    *Plots a matrix that allows for a quick inspection of nullity distribution and a 
    dendrogram to more accurately correlate variable completion. To interpret this graph:
        -read it from a top-down perspective
        -cluster leaves linked together at a distance of zero fully predict one another's presence
        -cluster leaves which split close to zero, but not at it, predict one another very well, but still imperfectly.
        -the height of the cluster leaf tells you, in absolute terms, how often the records are "mismatched" or 
        incorrectly filled—that is, how many values you would have to fill in or drop, if you are so inclined.
    
    """
    df = dfr.read_file_path(file_path)
    df.dropna(subset=['co2_emissions_tonne'], inplace=True)
    msno.matrix(df)
    msno.dendrogram(df)



def knn_fill(file_path):
    """
    *Reads in dataset from path.
    
    *Drops NAs based on co2_emissions_tonne column.
     
    *Provides the sum of missing values per column.
    
    *Imputes missing values based on a kNN algorithm.
        -k indicates the number of nearest rows which have a feature to fill in each row's missing features
        -k neighbors are chosen based on some distance measure and their average is used as an imputation estimate.
    """
    
    np.random.seed(7)
    
    #reading dataset
    df = dfr.read_file_path(file_path)
    
    #dropping NAs based on co2_emissions_tonne column
    df.dropna(subset=['co2_emissions_tonne'], inplace=True)
    
    #dropping plant_type as it is still empty
    #remove this line once plant_type has been populated
    df.drop(['plant_type'], axis=1, inplace=True)
    
    #checking updated missing values
    print(df.isna().sum())
    
    #retaining column names
    df_fill_cols = list(df)
    
    #choosing the best k for the dataset
    #code adapted from:
    # https://towardsdatascience.com/handling-missing-values-in-machine-learning-part-2-222154b4b58e
    # https://www.kaggle.com/athi94/investigating-imputation-methods/notebook
    
    kvals = np.linspace(1, 100, 20, dtype='int64')
    
    #need to add 'plant_type' when populated
    Xcol=['country','year','emission_species','emission_accounting_scope','capacity_mw','primary_fuel',
          'generation_gwh','commissioning_year','latitude','longitude','unit_count']
    
    X = df[Xcol]
    Y = df.co2_emissions_tonne
    
    #baseline
    #regression problem given that the output is a numerical variable
    #using random forest regressor (could also use gradient boosting)
    rf = RandomForestRegressor(n_estimators=1000,max_depth=None, min_samples_split=10)
    
    #kNN imputation testing different values for k
    knn_errs=[]
    for k in kvals: 
        knn_err=[]
        X_knn = KNN(k=k, verbose=False).fit_transform(X)
        knn_err = cross_val_score(rf,X_knn, Y, cv=10, n_jobs=-1).mean()
        
        knn_errs.append(knn_err)
        print("[KNN] Estimated RF Test Error (n = {}, k = {}, 10-fold CV: {})".format(len(X_knn), k, np.mean(knn_err)))
        
    sns.set_style("darkgrid")
    _ = plt.plot(kvals, knn_errs)
    _ = plt.xlabel('K')
    _ = plt.ylabel('10-fold CV Error Rate')
    
    knn_err = max(knn_errs)
    k_opt = kvals[knn_errs.index(knn_err)]
    
    Xknn = KNN(k=k_opt, verbose=False).fit_transform(X)
    Yknn = Y
    
    print("[BEST KNN] Estimated RF Test Error (n = {}, k = {}, 10-fold CV): {}".format(len(Xknn), k_opt, np.mean(knn_err)))
     
    #dataset imputing 
    df_knn = pd.DataFrame(KNN(k=k_opt, verbose=False).fit_transform(df))
    df_knn.columns = df_fill_cols
    
    return df_knn

