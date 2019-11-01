import pandas as pd
import numpy as np
from sklearn import metrics
import matplotlib.pyplot as plt
from tensorflow import keras
import math

def actual_vs_estimated_scatter(df, actual_col, prediction_col, model_name, transform = None):



    def logarithm(inputs):
        return np.log(inputs)


    transformation = {'log':logarithm}

    
    def up_scaling(t):
        n = 1
        while (t > 10):
            t /= 10
            n *= 10
        n *= math.ceil(t)
        return n
    
    if transform is None:
        actual = df[actual_col]
        pred = df[prediction_col]
    else:
        if transform not in transformation:
            raise ValueError("{} is not a valid transformation".format(transform))
        else:
            actual = transformation[transform](df[actual_col])
            pred = transformation[transform](df[prediction_col])

    scale = [0,up_scaling(max(actual.max(), pred.max()))]

    plt.figure(figsize = (10,8))
    plt.scatter(actual,pred)
    plt.plot(scale,scale,'r')
    plt.title('Actual VS Estimated ({})'.format(model_name),fontsize=15)
    plt.xlabel('Actual Values', fontsize=15)
    plt.ylabel('Estimated Values', fontsize=15)

    
    
def accuracy_by_size(df, actual_col, prediction_col):
    capacity_cut_offs = list(range(0,4000,100))
    # baseline_mae = []
    # baseline_rmse = []
    prediction_mae = []
    prediction_rmse = []

    for capacity_cut_off in capacity_cut_offs:
        gppd_sub = df[df['capacity_mw'] > capacity_cut_off]
        prediction_mae.append(metrics.mean_absolute_error(gppd_sub[prediction_col],gppd_sub[actual_col]))
        prediction_rmse.append(np.sqrt(metrics.mean_squared_error(gppd_sub[prediction_col],gppd_sub[actual_col])))

    plt.figure(figsize = (10,8))

    mae_color = 'tab:red'
    rmse_color = 'tab:blue'

    plt.xlabel('Capacity Cutoff (MW)', fontsize = 15)
    plt.ylabel('MAE',fontsize = 15)
    plt.plot(capacity_cut_offs,prediction_rmse,color = rmse_color,label = 'RMSE Prediction')
    plt.plot(capacity_cut_offs,prediction_mae,color = mae_color,label = 'MAE Prediction')
    plt.legend(loc='center')
    plt.ylabel("")
    plt.title("Model Accuracy by Plant Size", fontsize=15)
    
    
    
def error_distribution(df,gap_col_name,pred_col_name,bins):
    df.sort_values(by=pred_col_name,inplace=True)
    df.reset_index(drop=True, inplace=True)
    plt.figure(figsize=(8,6))
    df[gap_col_name].hist(bins = bins)
    plt.ylabel('Count',fontsize = 15)
    plt.xlabel('Prediction Error',fontsize = 15)



def model_evaluation_keras(model, weights_path, test_x, test_y, test_x_scaled = None, scaler = None, transform = None):
    if test_x_scaled is not None:
        assert scaler is not None,"To inverse scale the y value, you have to provide a scaler as well"
        
    # Load model weights
    model.load_weights(weights_path)
    
    # Predict values for the test set
    if test_x_scaled is None:
        y_pred = model.predict(test_x)
    else:
        y_pred = scaler.inverse_transform(model.predict(test_x_scaled))
    
    # Copy the test set to store predicted values
    results_df = test_x.copy()
    pred_col_name = 'prediction_co2_emissions'
    pred_clipped_col_name = 'prediction_co2_emissions_clipped'
    act_col_name = 'co2_emissions'
    residual_col_name = 'residual(pred - act)'
    error_rate_col_name = 'error_rate'
    
    results_df[pred_col_name] = y_pred
    results_df[act_col_name] = test_y
    # results_df[pred_clipped_col_name] = results_df[pred_col_name].apply(lambda x: 0 if x < 0 else x)
    results_df[residual_col_name] = results_df[pred_col_name] - results_df[act_col_name]
    results_df[error_rate_col_name] = results_df[residual_col_name] / results_df[act_col_name]
    
    print('Model performance on testset:\n')
    print('Coefficient of Determination - {}'.format(metrics.r2_score(y_pred,test_y)))
    print('MAE - {}'.format(metrics.mean_absolute_error(y_pred,test_y)))
    print('RMSE - {}'.format(np.sqrt(metrics.mean_squared_error(y_pred,test_y))))
    
    actual_vs_estimated_scatter(results_df,act_col_name,pred_col_name,'Neural Network', transform = transform)
    # accuracy_by_size(results_df, act_col_name, pred_clipped_col_name)
    error_distribution(results_df, error_rate_col_name, pred_col_name, bins = 50)
    
    return results_df










