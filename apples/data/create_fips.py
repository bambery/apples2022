import os
import csv
import pandas as pd

#local imports
import shared.utils as utils

resources = utils.get_resource_dir() 
file_path_fips = resources.joinpath("fips_by_date", "state_and_county_fips_master.csv")
file_path_city_county = resources.joinpath("cities_by_county", "us_cities_states_counties.csv")



#US_STATES = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE',
#        'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 
#        'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 
#        'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'MD', 
#        'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD',
#        'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
US_STATES = { 'ALASKA':'AK','ALABAMA': 'AL', 'ARKANSAS':'AR', 'ARIZONA': 'AZ', 'CALIFORNIA':'CA',
        'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'WASHINGTON DC':'DC', 'DELAWARE': 'DE', 
        'FLORIDA': 'FL', 'GEORGIA': 'GA', 'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 
        'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 
        'NEBRASKA': 'NE', "NEVADA": 'NV', 'NEW HAMPSHIRE': 'NH', 
        'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 
        'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK', 'OREGON': 'OR', 'MARYLAND': 'MD', 
        'MAINE': 'ME', 'MONTANA': 'MT', 'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 
        'MISSISSIPPI': 'MS', 'MISSOURI':'MO', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 
        'SOUTH CAROLINA': 'SC', 'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT',
        'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 
        'WYOMING': 'WY' }
def get_fips():
    df = pd.read_csv(file_path_fips,
            header=0,
            names=['fips', 'county', 'state'])
    # delete rows with "NA" or "NaN" values in state column
    df = df.dropna().reset_index(drop=True)

    # upcase name for comparison
    df['county']= df['county'].str.upper()
    # remove "County", "Census Area", "Borough"
    df['county'] = df['county'].str.removesuffix(' COUNTY')
    df['county'] = df['county'].str.removesuffix(' CENSUS AREA')
    df['county'] = df['county'].str.removesuffix(' BOROUGH')
    df['county'] = df['county'].str.removesuffix(' MUNICIPALITY')
    df['county'] = df['county'].str.removesuffix(' PARISH')
    df['county'] = df['county'].str.removesuffix(' AND')

    # should handle Juneau's strange county name here - the "city" is not wanted for once in the county name

    return df

# NOTE: It is right here in get_city_counties() that I am making the choice to prioritize one county over another, when one city
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
    df = pd.read_csv(file_path_city_county, 
            sep="|", 
            header=0,
            names=['city', 'state', 'state_long', 'county', 'city_alias'],
            # For now, it seems capable of intelligently selecting the chronologically first entry from the input file.
            #   The input file is ordered by some unknown sorting mechanism which selected the "best" county for each city, 
            #   almost but not always based on geographical overlap with county maps (charlottesville, SC is one such 
            #   exception, see note below) 
            # If it ever begins to misbehave, I can reject known cities with multiple counties and manually add them in, using the designations listed above this method
            usecols=['city', 'state', 'county']).drop_duplicates(keep='first', subset=['city', 'state'])
    # drop any PR or other rows not in the official 50 states (plus DC, which has a unique fips of 11001)
    df = df[df.state.isin(utils.US_STATES.values())]
    df.reset_index(drop=True)
    # upcase city name for comparison
    df['city'] = df['city'].str.upper()
    return df

    

# method: get_airports_cities() - 
# - this method begins with the list of airports with city and state
# - the method then associates the city/state with a county name
# - then associates the county with a fips code

# 1. read in list of airports [col num]- includes city/state [combined mess in 0], IATA [2], role(hub designation) [5], enplanements [6]
#   - input is divided by state, with one row containing the state name, followed by the rows of airports in this state, then the next state name...
#   - input contains entries for US territories, and must be filtered by 50 states + DC
#   - certain airports are assigned to two cities - choose the first
#   - DC and Hawaii have entries in a slightly different format and must be handled separately.
# 2. associate city/state with a county
#   - as with city name, sometimes there is more than one way to designate a name
#   - names can have different shortenings - (Saint, St, St., Sainte, Ste., Ste)
#   - sometimes some names will have dashes between one or more words
# 3. to do:
#   - strip all punctuation from a name
#   - if "saint" or "st" appear ( now stripped of punctuation), choose "saint"
#   - if "sainte" or "ste" appear, choose "Sainte"
#   - finally, strip all whitespace

normalized = []

def get_airports_cities():
    # going to manually wrangle this one
    # special cases: hawaii, washingtondc
    # constructing the data object this way for easy transfer to pandas - list of lists, where the first list is col headers and all subsequent are rows
    ans = [['city', 'state', 'county', 'fips', 'iata', 'role']]
    if os.path.exists(file_path_airports_cities):
        with open(file_path_airports_cities, "r", newline='') as file:
            reader = csv.reader(file, delimiter=",")
            header = next(reader)
            state = 'AL' # setting default
            for row in reader:
                county = '' # empty out county
                my_fips = '' # empty
                city = row[0]
                city = utils.normalize_name(city)

                iata = row[2]
                airport = row[4]
                role = row[5]
                # the file contains territorries as well as states - we are not looking at these right now.
                if city == "AMERICAN SAMOA": # we are done
                    break
                if (not iata): # we are in a state header row 
                    state_name = city
                #if city.startswith('PAGO'): # another attempt to catch American Samoa - is it still possible to reach here? #TODO
                    if not US_STATES.get(state_name):
                        continue # skip row if not us state # why are there 3 attempts to catch non-us states? #TODO
                    state = US_STATES[state_name]
                    continue # we have grabbed the state header
                elif iata in ['DCA', 'IAD']: # DC needs to be manually handled
                    state = 'DC'
                    city = 'WASHINGTON DC'
                    #TODO: continue handling this case
                    continue
                normalized.append(foo)
                if city.find("/"):
                    city = city.partition('/')[0].rstrip()# if the airport has a dual city, choose the first
                if state == "HI": # hawaii's entries are quoted, I assume to contain the island name
                    city = city.partition(',')[0].rstrip()
                    if iata == 'KOA': # omg this time it is city/county that is missing a dash where airport has one
                        # I don't like this fix since it seems like the city itself as an entity prefers the dash but shrug
                        city = 'KAILUA KONA'
                if state == 'AK': # handling Alaska's special cases
                    # Deadhorse is not technically a city, and I guess wasn't in the cities csv
                    if city == 'DEADHORSE':
                        ans.append([city, state, 'NORTH SLOPE', 2185, iata, role])
                        continue
                    elif city == 'KLAWOCK':
                        # county Prince of Wales Hyder is "Wales-Hyder' per fips csv
                        ans.append([city, state, 'PRINCE OF WALES-HYDER', 2198, iata, role])
                        continue
                    elif city == "ST. MARY'S":
                        ans.append([city, state, 'WADE HAMPTON', 2270, iata, role]) # why no dash in county?
                        continue
                    elif city.startswith('UTQ'): # this city is referred to as "Barrow" in fips, in defiance of the city itself
                        ans.append(['BARROW', state, 'NORTH SLOPE', 2185, iata, role]) # city/county doesnt have "city" 
                        continue
                if state == 'CA':
                    if iata == 'ACV': 
                        city = 'MCKINLEYVILLE' # the aiports csv shows name of this airport (Arcata/Eureka) as the city, which is actually McKinleyville
                    if iata == 'SNA': # serves 'orange county' but airport is in santa ana
                        city = 'SANTA ANA'
                if state == 'CO':
                    if iata == 'EGE':
                        city = "EAGLE" # doesn't matter which city is chosen, both in Eagle County
                if state == 'FL':
                    if iata == 'PIE':
                        city = 'SAINT PETERSBURG'
                if state == 'IL':
                    if iata == 'BLV':
                        ans.append([city, state, 'ST. CLAIR', 17163, iata, role]) # st vs saint, this time in county
                        continue
                if state == 'IN': # more saints
                    if iata == 'SBN':
                        ans.append([city, state, 'ST. JOSEPH', 18141, iata, role]) # st vs saint, this time in county
                        continue
                if state == 'KY': # on a combined city, the first listed was actually not in the given state - its a municipal zone
                    if iata == 'CVG':
                        ans.append(['COVINGTON', state, 'KENTON', 21117, iata, role]) # cincinatti tri-state area not being captured here 
                        continue
                if state == 'MI':
                    # unsure what to do with city name 'SAULT STE. MARIE' in airport
                    # name in city/county: 'Sault Sainte Marie'
                    # county in city/county: CHIPPEWA
                    if iata == 'CIU':
                        ans.append(['SAULT SAINTE MARIE', state, 'CHIPPEWA', 26033, iata, role]) # cincinatti tri-state area not being captured here 
                        continue
                if state == 'MN':
                    if iata == 'DLH': # another st vs saint
                        ans.append(['DULUTH', state, 'ST. LOUIS', 27137, iata, role]) # cincinatti tri-state area not being captured here 
                        continue
                    if iata == 'HIB': # another st vs saint
                        ans.append(['HIBBING', state, 'ST. LOUIS', 27137, iata, role]) # cincinatti tri-state area not being captured here 
                        continue
                    if iata == 'MSP': # minneapolis-saint paul
                        city = 'MINNEAPOLIS'
                    if iata == 'STC':
                        city = 'SAINT CLOUD'
                if state == 'MO':
                    if iata == 'STL':
                        ans.append(['SAINT LOUIS', state, 'ST. LOUIS', 29189, iata, role]) # cincinatti tri-state area not being captured here 
                        continue
                if state == 'NJ':
                    if iata == 'EWR': # jersey can keep newark (this is another culprit of the second of two cities being preferred
                        city = 'NEWARK'
                if state == "NY":
                    if iata == 'OGS': # another saint county
                        ans.append(['OGDENSBURG', state, 'ST. LAWRENCE', 36089, iata, role]) # cincinatti tri-state area not being captured here 
                        continue
                if state == 'PA':
                    if iata == 'AVP':
                        city = "WILKES BARRE" # entry has dash in airports, no dash in city/county
                if state == 'SC':
                    if iata == 'HHH':
                        city = 'HILTON HEAD ISLAND'
                if state == 'TN':
                    if iata == 'TRI':
                        city = 'BLOUNTVILLE'
                if state == 'UT':
                    if iata == 'SGU':
                        city = "SAINT GEORGE"

                # find the county for this location
                test_county = cities.loc[(cities['state'] == state) & (cities['city'] == city)]['county']
                if not test_county.empty: # nothing untoward here
                    county = test_county.values[0]
                else: 
                    dashed_city = city.replace(' ', '-') # didn't find it, let's try adding dashes, see if that does it
                    test_county = cities.loc[(cities['state'] == state) & (cities['city'] == dashed_city)]['county']
                    if not test_county.empty: # this county name needs a dash in place of whitespace
                        county = test_county.values[0]
                    else: # truly something has gone wrong
                        print("inside county")
                        print("something has gone wrong *********")
                
                # find the fips for this location
                test_fips = fips.loc[(fips['state'] == state) & (fips['county'] == county)]['fips']
                if not test_fips.empty: # nothing untoward here
                    my_fips = test_fips.values[0]
                else: 
                    dashed_county = county.replace(' ', '-')
                    test_fips = fips.loc[(fips['state'] == state) & (fips['county'] == dashed_county)]['fips']
                    if not test_fips.empty: # this county name needs a dash in place of whitespace
                        my_fips = test_fips.values[0]
                    else: # we can try one more thing for the county name - sometimes city/county omits "city" in the county name for blended
                        city_county = county + " CITY"
                        test_fips = fips.loc[(fips['state'] == state) & (fips['county'] == city_county)]['fips']
                        if not test_fips.empty: # this county name needs a dash in place of whitespace
                            my_fips = test_fips.values[0]
                        else: # we can try one more thing for the county name 
                            # truly something has gone wrong
                            print(" inside fips")
                            print("something has gone wrong *********")
                ans.append([city, state, county, my_fips, iata, role]) 
    return ans

#cities = get_city_counties()
#fips = get_fips()
#airports = get_airports_cities()
#breakpoint()
