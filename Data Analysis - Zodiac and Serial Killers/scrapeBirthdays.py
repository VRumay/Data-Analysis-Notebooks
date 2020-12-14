import urllib3
from googlesearch import search
import pandas as pd
import numpy as np
import pyreadr
import requests
from bs4 import BeautifulSoup
import wikipedia
import re


# Data from:
# https://github.com/lhehnke/serial-killers/

# Wallpaper from:
# https://wallpaperaccess.com/hd-stars 


#-----

# Convert R studio data to a pandas dataframe
result = pyreadr.read_r('serial_killers_data.rds')
killers = result[None]

# List from 'name' column
names = killers['name'].to_list()

# Catcher list for biographies
bioFile = []

# Iterate over the list of names and return the first website that comes up in google search about their birthday
# I was trying to figure out which ones had a wikipedia page.
for name in names:
    response= search(f"{name} birthday", num_results=0)
    if len(response) > 0:
        bioFile.append(response)
    else:
        bioFile.append('Missing Data')  

# Create a new column with the website that has their birthday info  
killers['bio'] = bioFile
killers['bio'] = killers['bio'].str.replace("['",'', regex=False).str.replace("']",'', regex=False)



# Once I had their bio links, I started querying wikipedia for the data, birthdays are usually in the first sentence, so that was all I needed to get fromt here

# Another catcher for summaries
summaries = []

# Iterate over their names and search in wikipedia to query the first sentence in their article
for eachKiller in names: 
    try:
        summary = wikipedia.summary(eachKiller, sentences=1)
    except:
        summary = 'not in wikipedia'
        pass        
    summaries.append(summary)

# Turn the catcher into a column
killers['summary'] = summaries

# Start mapping the dates from the summaries

# Define a month mapper (name to number)
month_map = dict(zip(
    ['january','february', 'march', 'april', 'may', 'june', 'july',
     'august', 'september', 'october', 'november', 'december'],
    range(1,13)
))

# Extract the first month name and map them to the correspondent number
killers['birth_month'] = (killers['summary'].astype(str).str.lower() # set strings to lower
                .str.findall('|'.join(month_map.keys())) # extract all available months
                .map(lambda x: x[0] if len(x)>0 else 0) # Extract just the first one
                .map(month_map)  # map them to its number
)

# Catcher to get all numbers in the summary
numbers = []

# iterate over summaries and extract a list of numerical characters found
for i in summaries:
    allnums = re.findall(r'\d+', str(i))
    numbers.append(allnums)

# Turn the catcher into a column
killers['numbers'] = numbers

killers['numbers'] = killers['numbers'].astype(str).str.replace('[','').str.replace(']','').str.replace("'","")

# Make an iterable from that column 
strNumbrs = killers['numbers'].to_list()

# Build two more catchers, one for year and one for days
days = []
years = []

# Split each string in the strNumbers iterable, if it's not possible, append a blank value 
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

# Turn catchers into columns
killers['birth_day'] = days
killers['birth_year'] = years

# Some filtering to make sure I wasn't getting death data instead of birth data.
killers['birth_month'] = np.where(killers['birth_day'].astype(str).str.len() > 2, '', killers['birth_month'])
killers['birth_month'] = np.where(killers['birth_month'].astype(str) == 'nan', '', killers['birth_month'])
killers['birth_day'] = np.where(killers['birth_day'].astype(str).str.len() == 1, '0' + killers['birth_day'] , killers['birth_day'])
killers['birth_day'] = np.where(killers['birth_day'].astype(str).str.len() > 2, '', killers['birth_day'])
killers['birth_year'] = np.where((killers['birth_year'].astype(str).str.len() > 4) & (killers['birth_month'] != ''), killers['birth_year'], '' )

# Drop unnecessary columns
del killers['numbers']

# Create a new column and map conditions to find out each killer's zodiac sign 
# I learned that there's more than one date/sign mapping, this one is the traditional one called 'tropical zodiac'
# Used https://en.wikipedia.org/wiki/Zodiac 
killers['tropical_zodiac_sign'] = np.where(((killers['birth_month'].astype(str) == '1.0') & (killers['birth_day'].astype(str) >= '20.0')) | 
                                           ((killers['birth_month'].astype(str) == '2.0') & (killers['birth_day'].astype(str) <= '19.0')), 'Aquarius',
                                  np.where(((killers['birth_month'].astype(str) == '2.0') & (killers['birth_day'].astype(str) >= '20.0')) | 
                                           ((killers['birth_month'].astype(str) == '3.0') & (killers['birth_day'].astype(str) <= '20.0')), 'Pisces',
                                  np.where(((killers['birth_month'].astype(str) == '3.0') & (killers['birth_day'].astype(str) >= '21.0')) | 
                                           ((killers['birth_month'].astype(str) == '4.0') & (killers['birth_day'].astype(str) <= '19.0')), 'Aries',
                                  np.where(((killers['birth_month'].astype(str) == '4.0') & (killers['birth_day'].astype(str) >= '20.0')) | 
                                           ((killers['birth_month'].astype(str) == '5.0') & (killers['birth_day'].astype(str) <= '20.0')), 'Taurus',
                                  np.where(((killers['birth_month'].astype(str) == '5.0') & (killers['birth_day'].astype(str) >= '21.0')) | 
                                           ((killers['birth_month'].astype(str) == '6.0') & (killers['birth_day'].astype(str) <= '20.0')), 'Gemini',
                                  np.where(((killers['birth_month'].astype(str) == '6.0') & (killers['birth_day'].astype(str) >= '21.0')) | 
                                           ((killers['birth_month'].astype(str) == '7.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Cancer',
                                  np.where(((killers['birth_month'].astype(str) == '7.0') & (killers['birth_day'].astype(str) >= '23.0')) | 
                                           ((killers['birth_month'].astype(str) == '8.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Leo',
                                  np.where(((killers['birth_month'].astype(str) == '8.0') & (killers['birth_day'].astype(str) >= '23.0')) | 
                                           ((killers['birth_month'].astype(str) == '9.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Virgo',
                                  np.where(((killers['birth_month'].astype(str) == '9.0') & (killers['birth_day'].astype(str) >= '23.0')) | 
                                           ((killers['birth_month'].astype(str) == '10.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Libra',
                                  np.where(((killers['birth_month'].astype(str) == '10.0') & (killers['birth_day'].astype(str) >= '23.0')) | 
                                           ((killers['birth_month'].astype(str) == '11.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Scorpio',
                                  np.where(((killers['birth_month'].astype(str) == '11.0') & (killers['birth_day'].astype(str) >= '23.0')) | 
                                           ((killers['birth_month'].astype(str) == '12.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Sagittarius',
                                  np.where(((killers['birth_month'].astype(str) == '12.0') & (killers['birth_day'].astype(str) >= '23.0')) | 
                                           ((killers['birth_month'].astype(str) == '1.0') & (killers['birth_day'].astype(str) <= '22.0')), 'Capricorn',''))))))))))))                                                                                    

# Save to CSV
killers.to_csv('serial_killers.csv', encoding='utf-8')

