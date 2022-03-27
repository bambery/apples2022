import os
import csv
import pandas as pd

source_file_fips = "../fips_by_state/state_and_county_fips_master.csv"
source_file_city_county = "../cities_by_county/us_cities_states_counties.csv"

# someday, look into pandas "converters" so I can clean inputs in the single read_csv statement

US_STATES = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE',
        'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 
        'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 
        'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'MD', 
        'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD',
        'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

def get_fips():
    df = pd.read_csv(source_file_fips,
            header=0,
            names=['fips', 'county', 'state'])
    # delete rows with "NA" or "NaN" values in state column
    df = df.dropna().reset_index(drop=True)
    # remove "county" and upcase name for comparison
    df['county'] = df['county'].str.removesuffix(' County').str.upper()
    return df

def find_city_fips(fips, cities):
    for index, row in cities.iterrows():
        try: 
            county_fips = fips.loc[(fips['name'] == row['county']) & (fips['state'] == row['state'])]
            cities.loc[index]['fips'] = county_fips['fips']
            breakpoint()
        except: 
            print("something went wrong")
            breakpoint()
#        breakpoint()
    return cities

# NOTE: It is right here in get_city_counties that I am making the choice to prioritize one county over another, when one city
#   is listed as having multiple counties
# I am going to manually choose for the roughly 30 cities by looking at maps - this only differs in one place from 
#   the default mechanism used currently
# AGS Augusta, GA: Richmond, 13245
# AMA Amarillo, TX: Potter, 48375
# ATL Atlanta, Georgia : Fulton, 13121
# AUS Austin, TX: Travis, 48453
# BHM Birmingham, AL: Jefferson, 1073
# BWI Baltimore, MD: Baltimore City, 16794
# CAE Columbia, SC: Richland
# CHO Charlottesville, VA: 82% of people employed here commute into the city, 42% of those from Albemarle County. An issue
#   the options are Charlottesville City county, or Albermarle County.
#   I will choose Charlottesville City County for the airport, Alberville will be captured by county proximity
# CHS Charleston, SC: Charleston
# CMH Columbus, OH: Franklin
# DAL Dallas, TX: Dallas County
# DFW Dallas, TX: Dallas County (Dallas/Forth Worth is another problem area)
# DAY Dayton, OH: Montgomery
# DEN Denver, CO: Denver
# FSD Sioux Falls, SD: Minnehaha
# HOU Houston, TX: Harris
# IAH Houston, TX: Harris
# IND Indianapolis, IA: Marion
# JAN Jackson, MS: Hinds
# JAX Jacksonville, FL: Duval
# LAN Lansing, MI: Ingham
# LCK Columbus, OH: Franklin
# MCI Kansas City, MO: Jackson
# MCO Orlando, FL: Orange
# MSY New Orleans, LA: Orleans
# OKC Oklahoma City, OK: Oklahoma (but significant areas spill over)
# OMA Omaha, NE: Lancaster
# PDX Portland, OR: Multnomah
# PHL Philidelphia, PA: Philideplhia
# RIC Richmond, VA: independent city (have not been indicating this) Richmond City
# ROA Roanoke, VA: independent city Roanoke City
# SAT San Antonio, TX: Bexar
# SQR Sarasota, FL: Sarasota
# TOL Toledo, OH: Lucas
# TTN Trenton, NJ: Mercer
# TUL Tulsa, OK: Tulsa

def get_city_counties():
    df = pd.read_csv(source_file_city_county, 
            sep="|", 
            header=0,
            names=['city', 'state', 'state_long', 'county', 'city_alias'],
            # For now, it seems capable of intelligently selecting the chronologically first entry from the input file.
            #   The input file is ordered by some unknown sorting mechanism which selected the "best" county for each city, 
            #   almost but not always based on geographical overlap with county maps (charlottesville, SC is one such 
            #   exception, see note below) 
            # If it ever begins to misbehave, I can reject known cities with multiple counties and manually add them in
            usecols=['city', 'state', 'county']).drop_duplicates(keep='first', subset=['city', 'state'])
    # drop any PR or other rows not in the official 50 states (plus DC, which has a unique fips of 11001)
    df = df[df.state.isin(US_STATES)]
    df.reset_index(drop=True)
    # upcase city name for comparison
    df['city'] = df['city'].str.upper()
    return df


def get_airports_cities():
    source = "../airport-cities/airport-cities.csv"
    df = pd.read_csv(source, 
            header=0, 
            names=['city', 'state', 'iata', 'role', 'enplanements'],
            usecols=['city', 'state', 'iata', 'role'])
    df['city'] = df['city'].str.upper()
    return df

def match_airport_city_county(cities, airports):
    city_multi = cities.set_index(['city', 'state'])
    airports_multi = airports.set_index(['city', 'state'])
    foo = airports_multi.join(city_multi, on=['city', 'state'], how='left')
    # dupes are the cities listed to multiple counties in the input file
    dupes = foo[foo.duplicated(['iata'])]
    breakpoint()

cities = get_city_counties()
airports = get_airports_cities()
fips = get_fips()
match_airport_city_county(cities, airports)
#find_city_fips(fips, cities)
breakpoint()
