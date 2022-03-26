import os
import csv
import pandas as pd

source_file_fips = "../fips_by_state/state_and_county_fips_master.csv"
source_file_city_county = "../cities_by_county/us_cities_states_counties.csv"

US_STATES = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE',
        'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 
        'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 
        'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'MD', 
        'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD',
        'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

def get_fips():
    df = pd.read_csv(source_file_fips)
    # delete rows with "NA" or "NaN" values in state column
    df = df.dropna().reset_index(drop=True)
    #TODO: remove "county" and upcase county name
    return df

def get_city_counties():
    #df = pd.read_csv(source_file_city_county, sep="|", columns=['City', 'State short', 'County'])
    df = pd.read_csv(source_file_city_county, 
            sep="|", 
            header=0,
            names=['city', 'state', 'state_long', 'county', 'city_alias'],
            usecols=['city', 'state', 'county']).drop_duplicates(keep='first')
    # drop any PR or other rows not in the official 50 states (plus DC, which has a unique fips of 11001)
    df = df[df.state.isin(US_STATES)]
    df.reset_index(drop=True)
    df['city'] = df['city'].str.upper()

