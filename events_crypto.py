# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 14:30:05 2021

@author: lenovosedat
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from Event import Event

df_returns = pd.read_pickle('returns.pkl')
df_returns= df_returns.rename(columns=str.lower)


file_name = 'listing_coinbase.xlsx'
xls = pd.ExcelFile(file_name)

# list all sheets in the file
sheet_names = xls.sheet_names

# to read first three sheets to dataframe:
df_main = pd.read_excel(file_name, sheet_name=sheet_names[0])
df_review = pd.read_excel(file_name, sheet_name=sheet_names[1])
df_add_feature = pd.read_excel(file_name, sheet_name=sheet_names[2])

# create events df
df_event1 = df_main[['Name', 'Symbol', 'Announcement']]
df_event2 = df_review[['Name', 'Symbol', 'Announcement']]
df_event3 = df_add_feature[['Name', 'Symbol', 'Announcement']]

#frames = [df_event1, df_event2, df_event3]
frames = [df_event1]


df_events = pd.concat(frames, ignore_index=True)
df_events= df_events.rename(columns=str.lower)
t0=120
t1=1
t2=12
t3=30

event_df = pd.DataFrame(columns=['crypto_name', 'event_date', 'car', 'bhar', 'error_variance'])

#initialize dictionary
my_dict = {}

#bancor,
count = -1 
for ind, row in df_events.iterrows():
    # exclude if there is no announcement date
    if ( str(row['announcement']) !='NaT' ) and ( row['name'].lower()!='bancor' ):
        event = Event(df_returns, row, t0,t1,t2,t3)
        if event.check_available_data():
            count += 1
            temp_car_array, temp_bhar_array = event.cum_abn_return()
            car = temp_car_array[-1]
            bhar = temp_bhar_array[-1]
            error_variance = event.err_var
            crypto_name = event.crypto_name
            event_date = event.event_date
            
            #adding event to event df
            new_row = {'crypto_name':crypto_name, 'event_date':event_date, 'car':car, 'bhar':bhar, 'error_variance':error_variance}
            #append row to the dataframe
            event_df = event_df.append(new_row, ignore_index=True)
            
            #historical abnormal returns
            hist_abn = event.samp_eps_data
            hist_abn = hist_abn.append(event.abn_return, ignore_index=True)
            
            #create relative-days
            a = event.df_est_window.dates.append(event.df_event_window.dates, ignore_index=True)-event.event_date
            abn_matrix = pd.DataFrame({'relative-days': a.dt.days})
            #locate in a dictionary
            my_dict[crypto_name] = {'relative-days': a.dt.days, 'hist_abn': hist_abn[crypto_name]}


##################################historical CAR plotting ####################

#initialize dates column
hist_car_matrix = pd.DataFrame({'dates': range(-7, t2)})           
for key in my_dict:
    temp_concat = pd.concat([my_dict[key]['relative-days'], my_dict[key]['hist_abn']], axis=1)
    hist_car_matrix = hist_car_matrix.merge(temp_concat, on='dates', how='left')
            
hist_abn = hist_car_matrix.iloc[:, 1:].mean(axis=1)

#event_window_relative_days= np.linspace(-t1, t2-1, num=len(car))     
#event_line_x = np.linspace(0, 0, num=len(car))     
#event_line_y = np.linspace(min(min(car),min(bhar))*0.9, max(max(car),max(bhar))*1.1, num=len(car))     
x_axis = np.arange(-7, t2, 1)
plt.plot(x_axis, hist_abn.cumsum())
plt.xticks(x_axis)
#plt.plot(event_line_x, event_line_y, 'k--')
plt.xlabel("Days relative to event date")
plt.ylabel("Average CAR")
plt.savefig('car-abnormal_returns.eps', format='eps', dpi=1200)
plt.show()

plt.savefig('car-abnormal_returns')





##################### drop outliers ##########################################
#IQR
Q1 = np.percentile(event_df['car'], 25, interpolation = 'midpoint') 
Q3 = np.percentile(event_df['car'], 75, interpolation = 'midpoint') 
IQR = Q3 - Q1
# Upper bound
upper = np.where(event_df['car'] >= (Q3+1.5*IQR))
# Lower bound
lower = np.where(event_df['car'] <= (Q1-1.5*IQR))
event_df.drop(upper[0], inplace = True)
event_df.drop(lower[0], inplace = True)
##############################################################################
             

nbr_days = t2+t1
sum_car = event_df['car'].sum()
sum_bhar = event_df['bhar'].sum() 
sum_error_variance = event_df['error_variance'].sum()
    
t_stat_car = sum_car/np.sqrt(nbr_days*sum_error_variance)
t_stat_bhar = sum_bhar/np.sqrt(nbr_days*sum_error_variance)            

plt.hist(event_df['car'], bins='auto') 
plt.xlabel("Cumulative abnormal returns [-1, 1]")
plt.ylabel("Frequency")
plt.savefig('car-abnormal_returns_hist.eps', format='eps', dpi=1200)

plt.show()           
    
        





















"""
for ind, row in df_events.iterrows():
    # exclude if there is no announcement date
    if str(row.announcement) !='NaT':
        crypto_name = row['name'].lower()
        event_date = row['announcement']
    temp_data = df_returns[['dates', 'bitcoin', crypto_name, 'rm']]
    #find index of corresponding event-date on temp_data    
    date_index = temp_data.dates[temp_data.dates==event_date].index[0]
    df_est_window = temp_data[(temp_data.index >= date_index-t0) & (temp_data.index < date_index-t1)].reset_index(drop=True).dropna()
    df_event_window = temp_data[(temp_data.index >= date_index-t1) & (temp_data.index < date_index+t2)].reset_index(drop=True)
    df_post_event_window = temp_data[(temp_data.index >= date_index+t2) & (temp_data.index < date_index+t3)].reset_index(drop=True)
    
    #regression 
    X = df_est_window[['rm', 'bitcoin']]
    y = df_est_window[[crypto_name]]
    reg = LinearRegression().fit(X, y)
    
    # number of obs - number of parameters to be estimated X.shape = (100,1) n_free=100-2=98
    n_free = X.shape[0] - (X.shape[1] + 1)
    # sample error variance in estimation window
    samp_eps_data = y - reg.predict(X) 
    err_var = np.power(samp_eps_data,2).sum()/n_free
    
    #prediction and abnormal returns
    X_event = df_event_window[['rm', 'bitcoin']]
    y_event = df_event_window[[crypto_name]]
    abn_return = y_event - reg.predict(X_event)
    
    #cumulative and buy-and-hold abnormal return
    car = [abn_return[crypto_name][0]]
    bhar = [abn_return[crypto_name][0]]
    for j in range(1, len(abn_return)):
        car_new = car[j-1] + abn_return[crypto_name][j]
        car.append(car_new)
        
        #geometric sum
        addt = (1+bhar[j-1])*(1+abn_return[crypto_name][j]) - 1
        bhar.append(addt)
        
    #plot BHAR and CAR against event window
    event_window_relative_days= np.linspace(-t1, t2-1, num=len(car))     
    event_line_x = np.linspace(0, 0, num=len(car))     
    event_line_y = np.linspace(min(min(car),min(bhar))*0.9, max(max(car),max(bhar))*1.1, num=len(car))     
    plt.plot(event_window_relative_days, car, label = 'CAR')
    plt.plot(event_window_relative_days, bhar, label = 'BHAR')
    plt.plot(event_line_x, event_line_y, 'k--')
    plt.xlabel("Days relative to event date")
    plt.ylabel("Cum / buy-and-hold abnormal returns")
    plt.legend()
    plt.show()
    
    
    break
"""