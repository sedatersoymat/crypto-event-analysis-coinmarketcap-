# -*- coding: utf-8 -*-
"""
This code retrieves all cryto-names, symbols, links for their historical data from coinmarketcap.
Before running the code, dont forget to change "current_number_pages" 
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import re
from itertools import groupby
import pandas as pd



current_number_pages = 55  #check first how many pages of currencies there are 

temp_name_list = []
temp_sym_list = []
temp_link_list = []


PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

for j in range(1,current_number_pages+1):
    

    driver.get("https://coinmarketcap.com/?page="+str(j))
    
    
    #driver.find_element_by_tag_name('body').text
    
    sleep(5)
    
    #scroll down the cursor slowly till the bottom of the page
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    
    for i in range(1, total_height, 5):
        driver.execute_script("window.scrollTo(0, {});".format(i))
    
    #retrieve names, symbols
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    temp_names = soup.findAll('p',{"class":"sc-1eb5slv-0 iJjGCS"})
    temp_syms = soup.findAll('p',{"class":"sc-1eb5slv-0 gGIpIK coin-item-symbol"})
    
    #retrieve links of the currencies
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile("(^/currencies)")}):
        links.append(link.get('href'))
    
    #erase those containing "markets", and then consecutive replicates
    links = [string for string in links if "/markets/" not in string]
    links = [x[0] for x in groupby(links)]
    links = [ "https://coinmarketcap.com" + x for x in links]
    
    #append all to desired lists
    for i in range(len(temp_names)):
        temp_name = temp_names[i].text
        temp_name_list.append(temp_name)
        
        temp_sym = temp_syms[i].text
        temp_sym_list.append(temp_sym)
        
        temp_link_list.append(links[i])


#write on csv file
data = {'names': temp_name_list,
         'symbols': temp_sym_list,
         'links': temp_link_list}

df = pd.DataFrame.from_dict(data)

FILE_NAME = "currencies_coinmarketcap.csv"
df.to_csv(FILE_NAME)
