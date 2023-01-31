# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 12:57:55 2021

@author: lenovosedat
CAR vs wide range of event windows
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from Event import Event
from scipy import stats


def match_events(event_df, my_dict):
    temp_my_dict = {}
    for index, row in event_df.iterrows():
        for key in my_dict:
            if (row['crypto_name']==key) and (row['event_date'].year == my_dict[key]['year']):
                temp_my_dict[key] = my_dict[key]
    return temp_my_dict       

def match_events2(event_df, df_events):
    temp_df_events = []
    for index, row in event_df.iterrows():
        for index2, row2 in df_events.iterrows():
            if (row['crypto_name']==row2['name'].lower()) and (row['event_date'].year == row2['announcement'].year):
                temp_df_events.append( {'name': row2['name'], 'symbol': row2['symbol'], 'announcement': row2['announcement']} )
    temp_df_events = pd.DataFrame(temp_df_events)
    temp_df_events = temp_df_events.drop_duplicates()
    temp_df_events.reset_index(drop=True, inplace=True)
    return temp_df_events




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

frames = [df_event1]
#frames = [df_event1, df_event2, df_event3]  #activate if you want to include extra events


df_events = pd.concat(frames, ignore_index=True)
df_events= df_events.rename(columns=str.lower)

t0=120
t1=1
t3=30
t2=2 #defined for droping outliers

##############################drop outliers based on window [-1,1]############
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
            
            #historical abnormal returns
            hist_abn = event.samp_eps_data
            hist_abn = hist_abn.append(event.abn_return, ignore_index=True)
            
            #create relative-days
            a = event.df_est_window.dates.append(event.df_event_window.dates, ignore_index=True)-event.event_date
            abn_matrix = pd.DataFrame({'relative-days': a.dt.days})
            #locate in a dictionary
            my_dict[count] = {'crypto_name': crypto_name, 'relative-days': a.dt.days, \
                               'car': car, 'error_variance': error_variance, \
                               'event_date': event_date, 'hist_abn': hist_abn[crypto_name]}
            
            

##################### drop outliers ##########################################
#create CAR list
car_list = []            
for key in my_dict:
    car_list.append(my_dict[key]['car'])

#IQR
Q1 = np.percentile(car_list, 25, interpolation = 'midpoint') 
Q3 = np.percentile(car_list, 75, interpolation = 'midpoint') 
IQR = Q3 - Q1

#exclude my_dic elemets if its CAR >= (Q3+1.5*IQR) or CAR <= (Q1-1.5*IQR)
t_my_dict = my_dict.copy()
for key in t_my_dict:
    if ( t_my_dict[key]['car']>= (Q3+1.5*IQR) ) or ( t_my_dict[key]['car']<= (Q1-1.5*IQR) ):
        del my_dict[key]

#names of my_dic
name_my_dic = []
for key in my_dict:
    name_my_dic.append(my_dict[key]['crypto_name'])        


##############################################################################
#list of desired info: interval, CAR, t-stats
info_list = []
for t2 in range(2,3):
    #bancor,
    count = -1 
    my_dict2 = {}
    for ind, row in df_events.iterrows():
        if ( str(row['announcement']) !='NaT' ) and ( row['name'].lower() in name_my_dic ):
            event = Event(df_returns, row, t0,t1,t2,t3)
            if event.check_available_data():
                count += 1
                temp_car_array, temp_bhar_array = event.cum_abn_return()
                car = temp_car_array[-1]
                bhar = temp_bhar_array[-1]
                error_variance = event.err_var
                crypto_name = event.crypto_name
                event_date = event.event_date
                
                #historical abnormal returns
                hist_abn = event.samp_eps_data
                hist_abn = hist_abn.append(event.abn_return, ignore_index=True)
                
                #create relative-days
                a = event.df_est_window.dates.append(event.df_event_window.dates, ignore_index=True)-event.event_date
                abn_matrix = pd.DataFrame({'relative-days': a.dt.days})
                #locate in a dictionary
                my_dict2[count] = {'crypto_name': crypto_name, 'relative-days': a.dt.days, \
                                   'car': car, 'error_variance': error_variance, \
                                   'event_date': event_date, 'hist_abn': hist_abn[crypto_name]}
        
####################################  main results, CAR, stats ###############################
my_dict3 = {}
for y in range(2016,2022):
    globals()['list_CAR_'+str(y)] = []
list_CAR_average = []

for key in my_dict2:
    for y in range(2016,2022):
        if my_dict2[key]['event_date'].year == y:
            globals()['list_CAR_'+str(y)].append(my_dict2[key]['car'])
            list_CAR_average.append(my_dict2[key]['car'])
            

pd.options.display.float_format = "{:.2f}".format
df_desc = pd.DataFrame([list_CAR_average, list_CAR_2016, list_CAR_2017, list_CAR_2018, list_CAR_2019,\
                      list_CAR_2020, list_CAR_2021]).T
               #columns =['CAR, 2016-2021', 'CAR, 2016', 'CAR, 2017', 'CAR, 2018', 'CAR, 2019', 'CAR, 2020', 'CAR, 2021']).T
a = df_desc.describe()
'''
temp_info = "[-1, {}] & {}  & {} & {} & {} & {}  & {} & {} & {} & {} & {} \\ [0.2cm] \relax".format(\
             t2-1, round(100*sum_car/count,2), round(t_stat_car,2),\
             round(100*sum_car_2018/count_2018,2), round(t_stat_car_2018,2),\
             round(100*sum_car_2019/count_2019,2), round(t_stat_car_2019,2),\
             round(100*sum_car_2020/count_2020,2), round(t_stat_car_2020,2),\
             round(100*sum_car_2021/count_2021,2), round(t_stat_car_2021,2))
info_list.append(temp_info)
 
#str(info_list).replace('\\','').replace("relax',","\relax").replace("'","")

'''








         