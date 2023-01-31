# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 21:25:32 2021

@author: lenovosedat
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class Event:
    """
    [t0, t1) --> estimation window
    [t1,t2) --> event window
    [t2,t3) --> post-event window
    """
    def __init__(self, df_returns, event, t0, t1, t2, t3, car=True, btc_included=True):
        self.df_returns = df_returns
        self.event = event
        self.t0 = t0
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.car = car
        self.btc_included = btc_included
    
    def check_available_data(self):
        self.crypto_name = self.event['name'].lower()
        self.event_date = self.event['announcement']
        
        temp_data = self.df_returns[['dates', 'bitcoin', self.crypto_name, 'rm']]
        #find index of corresponding event-date on temp_data    
        date_index = temp_data.dates[temp_data.dates==self.event_date].index[0]
        self.df_est_window = temp_data[(temp_data.index >= date_index-self.t0) & (temp_data.index < date_index-self.t1)].reset_index(drop=True).dropna()
        self.df_event_window = temp_data[(temp_data.index >= date_index-self.t1) & (temp_data.index < date_index+self.t2)].reset_index(drop=True)
        #df_post_event_window = temp_data[(temp_data.index >= date_index+self.t2) & (temp_data.index < date_index+self.t3)].reset_index(drop=True)
        
        self.X = self.df_est_window[['rm', 'bitcoin']]
        self.y = self.df_est_window[[self.crypto_name]]
        
        if self.y.shape[0]>=min(60,self.t0-self.t1):
            #and len(self.df_event_window)==self.t2+self.t1
            return True
    
    def cum_abn_return(self):
        reg = LinearRegression().fit(self.X, self.y)
        
        # number of obs - number of parameters to be estimated X.shape = (100,1) n_free=100-2=98
        n_free = self.X.shape[0] - (self.X.shape[1] + 1)
        # sample error variance in estimation window
        self.samp_eps_data = self.y - reg.predict(self.X) 
        self.err_var = np.power(self.samp_eps_data,2).sum()/n_free
        self.err_var = self.err_var[0]
        
        #prediction and abnormal returns
        X_event = self.df_event_window[['rm', 'bitcoin']]
        y_event = self.df_event_window[[self.crypto_name]]
        self.abn_return = y_event - reg.predict(X_event)
    
        #cumulative and buy-and-hold abnormal return
        car = [self.abn_return[self.crypto_name][0]]
        bhar = [self.abn_return[self.crypto_name][0]]
        for j in range(1, len(self.abn_return)):
            car_new = car[j-1] + self.abn_return[self.crypto_name][j]
            car.append(car_new)
            
            #geometric sum
            addt = (1+bhar[j-1])*(1+self.abn_return[self.crypto_name][j]) - 1
            bhar.append(addt)
        self.car = car
        self.bhar = bhar
        return self.car, self.bhar
    
    
    #plot BHAR and CAR against event window
    """
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
    """
    