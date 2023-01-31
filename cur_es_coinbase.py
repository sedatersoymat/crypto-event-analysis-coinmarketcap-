# -*- coding: utf-8 -*-
"""
This code 
1.) retrieves crypto-names that are available on coinbase exchange,
2.) inner merge coinbase cryptos on coinmarketcap cryptos

I manually changed "inner_join_listings.csv" at the end of this code so that Celo included and different currencies 
with the same symbol issues are fixed   
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd



current_number_pages = 3  #check first how many pages of currencies there are 

temp_name_list = []
temp_sym_list = []

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

for j in range(1,current_number_pages+1):
    

    driver.get("https://www.coinbase.com/price/s/listed?page="+str(j))
        
    sleep(5)
    
    #scroll down the cursor slowly till the bottom of the page
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    
    for i in range(1, total_height, 5):
        driver.execute_script("window.scrollTo(0, {});".format(i))
    
    #retrieve names, symbols
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    temp_syms = soup.findAll('span',{"class":"TextElement__Spacer-hxkcw5-0 cicsNy Header__StyledHeader-sc-1xiyexz-0 bjBkPh AssetTableRowDense__StyledHeader-sc-14h1499-14 AssetTableRowDense__StyledHeaderLight-sc-14h1499-15 AssetTableRowDense__TickerText-sc-14h1499-16 cdqGcC"})
    temp_names = soup.findAll('span',{"class":"TextElement__Spacer-hxkcw5-0 cicsNy Header__StyledHeader-sc-1xiyexz-0 kwgTEs AssetTableRowDense__StyledHeader-sc-14h1499-14 AssetTableRowDense__StyledHeaderDark-sc-14h1499-17 cWTMKR"})
    
   
    
    #append all to desired lists
    for i in range(len(temp_syms)):
        temp_sym = temp_syms[i].text
        temp_sym_list.append(temp_sym)
        
        temp_name = temp_names[i].text
        temp_name_list.append(temp_name)

#write on csv file
data = {'symbols': temp_sym_list,
        'names': temp_name_list}

df = pd.DataFrame.from_dict(data)

FILE_NAME = "currencies_coinbase.csv"
df.to_csv(FILE_NAME)


########################list listings in coinbase platform
df1 = pd.read_csv('currencies_coinbase.csv')
df2 = pd.read_csv('currencies_coinmarketcap.csv')  

inner_join_df= pd.merge(df1, df2, on='names', how='inner')

inner_join_df2= pd.merge(df1, df2, on='symbols', how='inner')


FILE_NAME = "inner_join_listings.csv"
inner_join_df2.to_csv(FILE_NAME)

#"inner_join_listings.csv" has been manually changed so that Celo included and different currencies with the same symbol issue are fixed  