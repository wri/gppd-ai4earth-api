import pandas as pd
import statsmodels.api as sm
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2,f_regression,mutual_info_regression


def feature_importance_score(df, X_cols, y_col):

    y = df[y_col]
    X = df[X_cols]

    #apply SelectKBest class to extract top 10 best features
    bestfeatures = SelectKBest(score_func=mutual_info_regression, k = 'all')
    fit = bestfeatures.fit(X,y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(X.columns)

    #concat two dataframes for better visualization 
    featureScores = pd.concat([dfcolumns,dfscores],axis=1)
    featureScores.columns = ['Specs','Score']  #naming the dataframe columns
    result = featureScores.nlargest(15,'Score').reset_index(drop=True)
    print(result)  #print 10 best features
    return result




def step_forward_feature_selection(df, X_cols, y_col):
    
    '''
    This function helps determine important features based on step forward method.
    
    ==============================
    
    parameters:
    
    df: a pandas dataframe
    X_cols: a list of columns 
    y_col: a single column
    '''
    def generate_r_squared_score(X,y):
        
        X = sm.add_constant(X)
        ols = sm.OLS(y,X).fit()
        return ols.rsquared_adj
        
    
    feature_size = len(X_cols)
    y_var = df[y_col]
#     X_pool = df[X_cols]
    
    used_features = []
    selected_df = pd.DataFrame()
    r_squares = []
    
    for loop in range(feature_size):
        loop_max_score = 0
        loop_max_feature = None
        
        for feature in X_cols:
            
            if feature in used_features:
                continue
            
            selected_df[feature] = df[feature]
            new_score = generate_r_squared_score(selected_df, y_var)
            selected_df.drop([feature],axis=1,inplace=True)
            
            if len(r_squares) > 0 and new_score <= r_squares[-1]:
                continue
            
            if new_score > loop_max_score:
                loop_max_score = new_score
                loop_max_feature = feature
            
        if loop_max_score == 0:
            break
        
        used_features.append(loop_max_feature)
        selected_df[loop_max_feature] = df[loop_max_feature]
        r_squares.append(loop_max_score)
        
    result = pd.DataFrame({'features':used_features,'r_squared':r_squares})
    print(result)
    return result




def regression_summary(df, X_cols, y_col):


    y = df[y_col]
    X = df[X_cols]
    X = sm.add_constant(X)

    ols = sm.OLS(y,X).fit()
    print(ols.summary())