import pandas as pd
import numpy as np 
import bs4
from urllib.request import urlopen as siterequest
from bs4 import BeautifulSoup as soup

killers = pd.read_csv('serial_killers.csv')

names = killers['name'].to_list()
lastNames = killers['surname'].to_list()

for first, last in zip(names, lastNames):
    url = f"https://www.google.com/search?q={first}+{last.replace(' ','+')}+birthday"
    # Connect to website, Get website HTML then close connection
    print(url)
    website = siterequest(url)
    websitehtml = website.read()
    page_soup = soup(websitehtml, "html.parser") 
    website.close()

    
# Dataframe to store data
column_names = ["productName", "productPrice", 'productLocation']
grid = pd.DataFrame(columns = column_names)

