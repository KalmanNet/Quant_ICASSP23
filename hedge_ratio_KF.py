# Kalman Filter Mean Reversion Strategy
import torch
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import statsmodels.tsa.stattools as ts
from Linear_KF_hedge import KalmanFilter
from Linear_sysmdl import System_Model
import datetime
from sklearn.linear_model import LinearRegression
from myUtils import *


os.environ['KMP_DUPLICATE_LIB_OK']='True'

if torch.cuda.is_available():
    dev = torch.device("cuda:0")  # you can continue going on here, like cuda:1 cuda:2....etc.
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    print("Running on the GPU")
else:
    dev = torch.device("cpu")
    print("Running on the CPU")

dataFolderName = 'HedgeRatio' + '/'
if not os.path.exists(dataFolderName):
    os.makedirs(dataFolderName)


train_size = 2000 ########################
traj_length = 500 ########################
Chan = 0 # Change data source
if Chan==0:
    df=pd.read_csv(dataFolderName+'forex1421'+'.csv', index_col='time')
    df_train = df.iloc[:train_size]
    df = df.iloc[train_size:]   
else:
    df=pd.read_csv(dataFolderName+'EWA_EWC'+'.csv')
    df['Date']=pd.to_datetime(df['Date'], format='%Y%m%d').dt.date # remove HH:MM:SS
    df.set_index('Date', inplace=True)
    x=df['EWA']
    y=df['EWC'].values
    delta=0.0001 # delta=1 gives fastest change in beta, delta=0.000....1 allows no change (like traditional linear regression).
    q2=delta/(1-delta)
    r2=0.001
    R_0 = torch.zeros((2,2))
    beta_0=torch.tensor([[0.], [0.]])

# max_delta, max_r2 = KF_train_grid(df_train)
training_set = train_set(df_train, train_size, train_size)
max_q, max_r = KF_train(training_set, df_train, train_size, train_size, dataFolderName)

# training_set = train_set(df_train, traj_length, train_size)
# max_q, max_r = KF_train(training_set, df_train, train_size, traj_length, dataFolderName)
max_delta, max_r2 = -1/(max_q**2+1)+1, max_r**2

print(max_delta, max_r2)

q2, r2, R_0, beta_0 = prepare_forex(df_train)

# cum_pnl_1 = KF_test(df, max_delta, max_r2, R_0, beta_0)
cum_pnl_2 = KF_test_with_approx_bollinger(df, max_delta, max_r2, R_0, beta_0)


np.save(dataFolderName+'cum_KF_approx_bollinger_gradient_high', cum_pnl_2) # cum_KF_approx_bollinger_grid_high cum_KF_approx_bollinger_gradient_high
