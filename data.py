import pandas as pd 
import streamlit as st
import urllib.request, json 
import area as ar
from cachetools import cached, TTLCache

plz_name = None
cases = None 

#Streamlit cache doesn't work here
@cached(cache = TTLCache(maxsize=1, ttl = 60*60*24))         
def load_data():
    #PLZ to Name Mapping
    plz_name = dict({})
    plz_area = dict({})
    with urllib.request.urlopen("https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_plz/PLZ_gen_epsg4326_F_KTZH_2020.json") as url:
        data = json.loads(url.read().decode())
        for feature in data['features']:
            plz = (feature['properties']['PLZ'])
            name = feature['properties']['Ortschaftsname']
            area = ar.area(feature['geometry'])/1e6
            if plz is not None and name is not None: 
                plz_name[str(int(plz))] = str(name)
                plz_area[str(int(plz))] = area
    
    plz_name['8403'] = 'Winterthur' #Some manual fixes
    plz_area['8403'] = plz_area['8400'] #8403 is not that much a valid postal area :-/


    cases = pd.read_csv('https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_plz/fallzahlen_kanton_ZH_plz.csv')
    cases  = cases[cases['PLZ'].str.len() == 4] #Remove anything that is not a PLZ
    
    #Absolute numbers
    cases['NewConfCases_7days_range'] = cases['NewConfCases_7days'].apply(lambda x: list(map(lambda s: int(s), str(x).split('-'))))
    cases['NewConfCases_7days_min'] = cases['NewConfCases_7days_range'].apply(lambda a: a[0])
    cases['NewConfCases_7days_max'] = cases['NewConfCases_7days_range'].apply(lambda a: a[1])
    cases['NewConfCases_7days_avg'] = .5*cases['NewConfCases_7days_max']+ 0.5*cases['NewConfCases_7days_min']

    cases['NewConfCases_7days_range_per10k'] = cases.apply(lambda row: list(map(lambda x: 10000*x/row['Population'], row['NewConfCases_7days_range'])), axis=1)
    cases['NewConfCases_7days_min_per10k'] = cases['NewConfCases_7days_range_per10k'].apply(lambda a: a[0])
    cases['NewConfCases_7days_max_per10k'] = cases['NewConfCases_7days_range_per10k'].apply(lambda a: a[1])
    cases['NewConfCases_7days_avg_per10k'] = .5*cases['NewConfCases_7days_max_per10k']+ 0.5*cases['NewConfCases_7days_min_per10k']
    
    cases['Date'] = pd.to_datetime(cases['Date'],utc=True)
    cases['Name'] = cases['PLZ'].apply(lambda plz: plz+' '+plz_name[plz])
    cases['Area'] = cases['PLZ'].apply(lambda plz: plz_area[plz])

    return cases

