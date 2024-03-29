import pandas as pd 
import streamlit as st
import urllib.request, json 
import area as ar
from cachetools import cached, TTLCache

plz_name = None
cases = None 

# Streamlit cache doesn't work here
@cached(cache = TTLCache(maxsize=1, ttl = 60*60*1))         
def load_data():
    #PLZ to Name Mapping
    plz_name = dict({})
    plz_area = dict({})
    districts = pd.read_csv('Districts.tsv',header=None, sep='\t')

    plz_district = dict([(str(i),str(v)) for i, v in zip(districts[0], districts[2])])
    with urllib.request.urlopen("https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_plz/PLZ_gen_epsg4326_F_KTZH_2020.json") as url:
        data = json.loads(url.read().decode())
        for feature in data['features']:
            plz = (feature['properties']['PLZ'])
            name = feature['properties']['Ortschaftsname']
            area = ar.area(feature['geometry'])/1e6
            if plz is not None and name is not None:
                plz_str =  str(int(plz))
                plz_name[plz_str] = str(name)
                plz_area[plz_str] = area
    
    plz_name['8403'] = 'Winterthur' #Some manual fixes
    plz_district['8403'] = 'Winterthur' #Some manual fixes
    plz_area['8403'] = plz_area['8400'] #8403 is not that much a valid postal area :-/


    cases = pd.read_csv('https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_plz/fallzahlen_kanton_ZH_plz.csv')
    cases  = cases[cases['PLZ'].str.len() == 4] #Remove anything that is not a PLZ
    
    #Absolute numbers
    cases['NewConfCases_7days_range'] = cases['NewConfCases_7days'].apply(lambda x: list(map(lambda s: int(s), str(x).split('-') if '-' in str(x) else [str(x).replace('+','')]*2 )))
    cases['NewConfCases_7days_range_str'] = cases['NewConfCases_7days']#.apply(lambda x: ' - '.join(list(map(lambda s: s, str(x).split('-')))))
    cases['NewConfCases_7days_min'] = cases['NewConfCases_7days_range'].apply(lambda a: a[0])
    cases['NewConfCases_7days_max'] = cases['NewConfCases_7days_range'].apply(lambda a: a[1])
    cases['NewConfCases_7days_avg'] = .5*cases['NewConfCases_7days_max']+ 0.5*cases['NewConfCases_7days_min']

    cases['NewConfCases_7days_range_per10k'] = cases.apply(lambda row: list(map(lambda x: 10000*x/row['Population'], row['NewConfCases_7days_range'])), axis=1)
    cases['NewConfCases_7days_range_str_per10k'] = cases.apply(lambda row: '-'.join(list(map(lambda x: str(10000*x/row['Population']), row['NewConfCases_7days_range']))), axis=1)
    cases['NewConfCases_7days_min_per10k'] = cases['NewConfCases_7days_range_per10k'].apply(lambda a: a[0])
    cases['NewConfCases_7days_max_per10k'] = cases['NewConfCases_7days_range_per10k'].apply(lambda a: a[1])
    cases['NewConfCases_7days_avg_per10k'] = .5*cases['NewConfCases_7days_max_per10k']+ 0.5*cases['NewConfCases_7days_min_per10k']
    
    cases['Date'] = pd.to_datetime(cases['Date'],utc=True)
    cases['Week_of_year'] = cases['Date'].dt.strftime('%Y-%W')
    cases['Name'] = cases['PLZ'].apply(lambda plz: plz+' '+plz_name[plz])
    cases['Area'] = cases['PLZ'].apply(lambda plz: plz_area[plz])
    cases['District'] = cases['PLZ'].apply(lambda plz: plz_district[plz])

    bezirk_data = pd.read_csv('https://raw.githubusercontent.com/openZH/covid_19/master/fallzahlen_bezirke/fallzahlen_kanton_ZH_bezirk.csv')
    bezirk_data ['District_Week'] = bezirk_data.apply(lambda row: row['District'].replace('Bezirk ','')+str(row['Year'])+'-'+str(row['Week']),axis=1)
    bezirk_new_death_map = dict([(str(i),str(v)) for i, v in zip(bezirk_data ['District_Week'], bezirk_data ['NewDeaths'])])

    cases['NewDeaths_in_district_in_week'] = cases.apply(lambda row: bezirk_new_death_map.get(row['District']+str(row['Week_of_year']),"0"),axis=1)

    return cases


if __name__=="__main__":
    data = load_data()
    print(set(data['NewDeaths_in_district_in_week']))