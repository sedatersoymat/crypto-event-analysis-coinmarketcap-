# -*- coding: utf-8 -*-
"""
This code creates a crypto-market index, excluding Bitcoin 
by using market cap and closing prices data.

Divisor is updated at the end of each month or if any crypto is delisted or disappeared from market. 
"""

import pandas as pd
import numpy as np


#import data from excel files

df_market_cap = pd.read_csv('market_cap.csv')
df_close_price = pd.read_csv('close_price.csv')

#manipulate df for date and np format
def format_df(df):
    #change the format of dates to datetime
    df.dates = pd.to_datetime(df.dates)
    
    #manipulate market cap
    for column in df.columns:
        if column != 'dates':
            #erase dollar sign
            df[column] = df[column].str[1:]
            #change string nan to numpy nan
            df[column].replace('nan', np.nan)
            #erase commas and convert to float number if they are not numpy nan
            df[column] = [float(i.replace(',','')) if type(i)==str else i for i in df[column]]
    #sort them by date in ascending order
    df = df.sort_values(by='dates', ascending=True).reset_index(drop=True)
    return df

df_market_cap = format_df(df_market_cap)
df_close_price = format_df(df_close_price)

#return the column names with numbers for given index
def col_w_numbers(df, ind):
    columns = []
    for column in df.columns:
        if column != 'dates' and column !='Bitcoin' and np.isnan(df[column][ind])==False:    
            columns.append(column)
    return columns

#return market index value for given close price, market cap and index
def m_index(df_m, df_c, columns, ind):
    tot_m_cap = df_m[columns].loc[ind].sum()
    sum_index = 0
    for column in columns:
        sum_index += df_c[column].loc[ind]*df_m[column].loc[ind]/tot_m_cap
    return sum_index            

#initiate market index
mar_index = []
divisor = 1
    
#initial column names and market index value
columns = col_w_numbers(df_market_cap, 0) 
m_index_value = m_index(df_market_cap, df_close_price, columns, 0)

mar_index.append(m_index_value)

for i in range(1, len(df_market_cap.dates)):
    try:
        #update divisor at the end of each month
        if df_market_cap.dates[i+1].day == 1:
            #calculate index
            m_index_value = m_index(df_market_cap, df_close_price, columns, i)/divisor
            #update column names based on the last day of the month
            columns = col_w_numbers(df_market_cap, i) 
            #update divisor after finding index
            new_index = m_index(df_market_cap, df_close_price, columns, i) 
            divisor = new_index/m_index_value
            
            mar_index.append(m_index_value)
        #update divisor if any crypto is delisted or disappeared from market
        elif any(np.isnan(df_market_cap[columns].loc[i]))==True:
            #update column names first 
            columns = col_w_numbers(df_market_cap, i)
            #update divisor based on previous index value
            temp_index = m_index(df_market_cap, df_close_price, columns, i-1) 
            divisor = temp_index/m_index_value
            m_index_value = m_index(df_market_cap, df_close_price, columns, i)/divisor
            
            mar_index.append(m_index_value)
        else:
            #calculate index
            m_index_value = m_index(df_market_cap, df_close_price, columns, i)/divisor
            
            mar_index.append(m_index_value)
    except Exception:
        #calculate index for the last date
        m_index_value = m_index(df_market_cap, df_close_price, columns, i)/divisor    
        mar_index.append(m_index_value)
                

################# create return dataframes   ##################################
#initiate return df
df_returns = pd.DataFrame(df_close_price)
#append market index
df_returns['rm'] = mar_index
#calc the percentage change
for col in df_returns.columns:
    if col!='dates':
        df_returns[col] = df_returns[col]/df_returns[col].shift()-1
        #df_returns[col] = np.log(df_returns[col]/df_returns[col].shift(1))
###############################################################################                

#before saving some cleaning is necessary [realized while running events_crypto.py]
df_returns = df_returns.rename(columns={"Origin Token": "Origin Protocol"})

#save returns as data pickle
df_returns.to_pickle('returns.pkl')        





        

        