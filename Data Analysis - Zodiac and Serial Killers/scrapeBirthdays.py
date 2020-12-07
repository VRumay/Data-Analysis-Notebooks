import urllib3
from googlesearch import search
import pandas as pd
import numpy as np
import pyreadr
import requests
from bs4 import BeautifulSoup
import wikipedia
import re


#https://github.com/lhehnke/serial-killers/

# result = pyreadr.read_r('serial_killers_data.rds')

# killers = result[None]

# names = killers['name'].to_list()

# bioFile = []

# for name in names:
#     response= search(f"{name} birthday", num_results=0)
#     if len(response) > 0:
#         bioFile.append(response)
#     else:
#         bioFile.append('Missing Data')    

  
# killers['bio'] = bioFile

# killers['bio'] = killers['bio'].str.replace("['",'', regex=False).str.replace("']",'', regex=False)


# summaries = []

# for eachKiller in names: 
#     print(eachKiller)
#     try:
#         summary = wikipedia.summary(eachKiller, sentences=1)
#     except:
#         summary = 'not in wikipedia'
#         pass        
#     summaries.append(summary)

# killers['summary'] = summaries

killers = pd.read_csv('killers.csv')

killers['summary'] = killers['summary'].to_list()

# Define a month mapper (name to number)
month_map = dict(zip(
    ['january','february', 'march', 'april', 'may', 'june', 'july',
     'august', 'september', 'october', 'november', 'december'],
    range(1,13)
))

# Extracting the first month name and map them to the correspondent number
killers['month'] = (killers['summary'].astype(str).str.lower() # set strings to lower
                .str.findall('|'.join(month_map.keys())) # extract all available months
                .map(lambda x: x[0] if len(x)>0 else 0) # Extract just the first one
                .map(month_map)  # map them to its number
)



summaries = killers['summary'].to_list()

numbers = []

for i in summaries:
    allnums = re.findall(r'\d+', str(i))
    numbers.append(allnums)

killers['numbers'] = numbers

killers['numbers'] = killers['numbers'].astype(str).str.replace('[','').str.replace(']','').str.replace("'","")

strNumbrs = killers['numbers'].to_list()


days = []
years = []

for i in strNumbrs:
    splat = i.split(",")
    try:
       day = splat[0]
       year = splat[1]
    except:
       day = ''
       year = ''
    
    days.append(day)
    years.append(year)

killers['day'] = days
killers['year'] = years

# Just a placeholder to help convert to int later on.
killers['month'] = killers['month'].fillna(0.5)

killers['month']  = np.where(killers['day'].astype(str).str.len() > 2, '', killers['month'].astype(int))
killers['day']  = np.where(killers['day'].astype(str).str.len() == 1, '0'+killers['day'] , killers['day'])
killers['day']  = np.where(killers['day'].astype(str).str.len() > 2, '', killers['day'])
killers['year'] = np.where((killers['year'].astype(str).str.len() > 4) & (killers['month'] != ''), killers['year'], '' )



cols = ['year', 'month', 'day']

killers['birth_date'] = killers[cols].apply(lambda row: '-'.join(row.values.astype(str)), axis=1)

killers['birth_date']  = np.where(killers['birth_date'].astype(str).str.len() < 7, '', killers['birth_date'])

killers['birth_date'] = np.where(killers['birth_date'].astype(str).str.contains('-0-'),'',killers['birth_date'])

killers['birth_date'] = killers['birth_date'].astype(str)

killers['birth_date'] = pd.to_datetime(killers['birth_date'], errors='coerce')

del killers['numbers']
del killers['month']
del killers['day']
del killers['year']

#killers['month'] = np.where(len(killers['numbers'].str.split(",")) > 1, killers['numbers'].str.split(",")[1],'No year')


killers.to_csv('test.csv', encoding='utf-8')

