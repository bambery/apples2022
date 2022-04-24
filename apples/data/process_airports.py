import os
import csv
import itertools
import pandas as pd # yes I will use dataframes just because I need to read in xls format. Seriously, reading in various formats of excel files is a nightmare in 2022. 

#local imports
import shared.utils as utils

resources = utils.get_resource_dir() 

file_path_fips = resources.joinpath("fips_by_date", "state_and_county_fips_master.csv")
file_path_airports_cities = resources.joinpath("airport-cities", "airports_wiki.csv")
file_path_cbsa_list1= resources.joinpath("cbsa_lists", "list1_2020.xls")
file_path_cbsa_list2= resources.joinpath("cbsa_lists", "list2_2020.xls")

# columns
# 0: CBSA code, 1: metro division code, 2: csa code, 3: cbsa title, 4: metro/micro designation, 5: metro division title, 6: csa title, 7. county/county equivalent, 8. state name, 9. FIPS state code, 10: FIPS county code, 11: central or outlying
def read_cbsa_lists():
    cbsas = pd.read_excel(file_path_cbsa_list1, skiprows = 2, header = 0, usecols = [0, 3, 4, 7, 8, 9, 10, 11], nrows = 1913, dtype = {'CBSA Code': str, 'FIPS State Code': str, 'FIPS County Code': str} )
    cbsas["State Name"] = cbsas["State Name"].map( lambda x: utils.US_STATES.get(x.upper()) )
    cbsas.rename(columns = {"State Name": "State"}, inplace = True)
    principal_cities = pd.read_excel( file_path_cbsa_list2, skiprows = 2, header = 0, usecols = [0, 2, 3, 4], nrows = 1269, dtype = {'CBSA Code': str, 'FIPS State Code': str}) 
    principal_cities["State"] = principal_cities["FIPS State Code"].map( utils.FIPS_US_STATE )

    return (cbsas, principal_cities)

def get_fips():
    df = pd.read_csv(file_path_fips,
            header=0,
            names=['fips', 'county', 'state'])
    # delete rows with "NA" or "NaN" values in state column
    df = df.dropna().reset_index(drop=True)
    df['county'] = df['county'].map(utils.normalize_name)

    # remove "County", "Census Area", "Borough"

    breakpoint()

    # should handle Juneau's strange county name here - the "city" is not wanted for once in the county name

    return df

fips = get_fips()

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


def get_airports_cities():
    # going to manually wrangle this one
    # special cases: hawaii, washingtondc
    # constructing the data object this way for easy transfer to pandas - list of lists, where the first list is col headers and all subsequent are rows

    cbsas, principal_cities = read_cbsa_lists() 

    ans = [['city', 'state', 'county', 'fips', 'iata', 'role', 'enplanements']]
    if os.path.exists(file_path_airports_cities):
        with open(file_path_airports_cities, "r", newline='') as file:
            reader = csv.reader(file, delimiter=",")
            header = next(reader)
            state = 'AL' # setting default
            for row in reader:
                county = None 
                my_fips = None 
                my_code = None 
                my_size = None
                city = row[0]
                city = utils.normalize_name(city)

                iata = row[2]
                airport = row[4]
                role = row[5]
                enplanements = row[6]
                # the file contains territorries as well as states - we are not looking at these right now.
                if city == "AMERICAN SAMOA": # we are done
                    break
                if (not role): # we are in a state header row 
                    state_name = city
                    if not utils.US_STATES.get(state_name):
                        raise Exception("can you even reach this still?")
                    state = utils.US_STATES[state_name]
                    # we have grabbed the state header
                elif not iata:
                    # Lake Hood Seaplane Base does not have an IATA, nor appear in the list of flights and will be discarded
                    continue # skip to next entry

                elif iata in ['DCA', 'IAD']: # DC needs to be manually handled
                    state = 'DC'
                    city = 'WASHINGTON DC'

                fips_lookup = {} 
                test_msa = principal_cities.loc[ (principal_cities["Principal City Name"].str.upper() == city) & (principal_cities["State"] == state) ]
                # check to see if metro/micropolitan area 
                if not test_msa.empty: # we found a cbsa
                    my_code = test_msa["CBSA Code"].squeeze()
                    my_size = test_msa["Metropolitan/Micropolitan Statistical Area"].squeeze()
                    if my_size.startswith("Metro"):
                        my_size = "METRO"
                    elif my_size.startswith("Micro"):
                        my_size = "MICRO"
                    df_test_fips = cbsas.loc[ cbsas["CBSA Code"] == my_code ]
                    state_fips = df_test_fips["FIPS State Code"].to_list()
                    county_fips = df_test_fips["FIPS County Code"].to_list()
                else: # no hits in principal_cities, instead lookup fips
                    test_fips = fips.loc[(fips['state'] == state) & (fips['county'] == county)]['fips']
                    if not test_fips.empty:
                        breakpoint()
                    else:
                        breakpoint()

                    # note that somewhere around here is where I would weed out "outlying" if I wanted

                    for (state, county) in itertools.zip_longest(state_fips, county_fips):
                        fips_lookup[state + county] = { "code": my_code, "size": my_size } 

                        '''

                # find the fips for this location
                breakpoint()
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
    #'''
    return ans
