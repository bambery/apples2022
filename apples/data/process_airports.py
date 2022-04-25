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
file_path_city_county = resources.joinpath("cities_by_county", "us_cities_states_counties.csv")

# columns
# 0: CBSA code, 1: metro division code, 2: csa code, 3: cbsa title, 4: metro/micro designation, 5: metro division title, 6: csa title, 7. county/county equivalent, 8. state name, 9. FIPS state code, 10: FIPS county code, 11: central or outlying
def read_cbsa_lists():
    cbsas = pd.read_excel(file_path_cbsa_list1, skiprows = 2, header = 0, usecols = [0, 3, 4, 7, 8, 9, 10, 11], nrows = 1913, dtype = {'CBSA Code': str, 'FIPS State Code': str, 'FIPS County Code': str} )
    cbsas["State Name"] = cbsas["State Name"].str.upper()
    # add new column for state abbreviation
    cbsas["State"] = cbsas["State Name"].map( utils.US_STATES )

    #cbsas.rename(columns = {"State Name": "State"}, inplace = True)

    principal_cities = pd.read_excel( file_path_cbsa_list2, skiprows = 2, header = 0, usecols = [0, 2, 3, 4], nrows = 1269, dtype = {'CBSA Code': str, 'FIPS State Code': str}) 
    principal_cities["State"] = principal_cities["FIPS State Code"].map( utils.FIPS_US_STATE )
    principal_cities["Principal City Name"] = principal_cities["Principal City Name"].map( utils.normalize_name)
    return (cbsas, principal_cities)

def get_fips():
    df = pd.read_csv(file_path_fips,
            header=0,
            names=['fips', 'county', 'state'])
    # delete rows with "NA" or "NaN" values in state column
    df = df.dropna().reset_index(drop=True)
    df['county'] = df['county'].map(utils.normalize_name)

    return df

# old notes about problem cities that drove the change from FIPs to CBSA:
# CHO Charlottesville, VA: 82% of people employed here commute into the city, 42% of those from Albemarle County. An issue
#   the options are Charlottesville City county, or Albermarle County.
#   I will choose Charlottesville City County for the airport, Alberville will be captured by county proximity
# DFW Dallas, TX: Dallas County (Dallas/Forth Worth is another problem area)
# OKC Oklahoma City, OK: Oklahoma (but significant areas spill over)

def get_city_counties():
    df = pd.read_csv(file_path_city_county, 
            sep="|", 
            header=0,
            names=['city', 'state', 'state_long', 'county', 'city_alias'],
            #   The input file is ordered by some unknown sorting mechanism which selected the "best" county for each city, 
            #   almost but not always based on geographical overlap with county maps (charlottesville, SC is one such 
            #   exception, see note below) 
            usecols=['city', 'state', 'county']).drop_duplicates(keep='first', subset=['city', 'state'])
    # drop any PR or other rows not in the official 50 states (plus DC, which has a unique fips of 11001)
    df = df[df.state.isin(utils.US_STATES.values())]
    df.reset_index(drop=True)
    # upcase city name for comparison
    df['city'] = df['city'].map(utils.normalize_name)
    return df




def get_airports_cities(fips):

    fips_lookup = {} 
    uids = {}

    # if cbsa_code is None, then there is no associated CBSA
    def associate_ids(fips, cbsa_code, airport:None):

        if cbsa_code:
            df_test_fips = cbsas.loc[ cbsas["CBSA Code"] == cbsa_code ]
            state_fips = df_test_fips["FIPS State Code"].to_list()
            county_fips = df_test_fips["FIPS County Code"].to_list()

            # since I am summing enplanements, I am going to drop the airport hub designation - can return if needed
            # STOPPING: need to check if key exists
            uids[cbsa_code] = {
                fips: [],
                airports: [],
                size: my_size,
                enplanements: 0
            # add entry to fips lookup
            }

            for (c_state, c_county) in itertools.zip_longest(state_fips, county_fips):
                # only the cbsa files use leading zeros - skip them for all other uses
                fips_code = (c_state + c_county).lstrip('0')
                if fips_code in fips_lookup:
                    # this fip already exists
                    # TODO: Task #13 - add enplanements as a sum of all airports within CBSA
                    continue

            fips_lookup[fips_code] = cbsa_code
            # add fips to list of fips for the associated CBSA
            if fips_code not in uids[cbsa_code][fips]: 
                uids[cbsa_code][fips].append(fips_code)
            if iata not in uids[cbsa_code][airports]:
                uids[cbsa_code][airports].append(iata)
        else: # this is a fips without a CBSA


    cbsas, principal_cities = read_cbsa_lists() 
    city_counties = get_city_counties()

    if os.path.exists(file_path_airports_cities):
        with open(file_path_airports_cities, "r", newline='') as file:
            reader = csv.reader(file, delimiter=",")
            header = next(reader)
            state = 'AL' # setting default
            # translation for fips to CBSA - gives FIPs if no CBSA
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
                    continue

                # Lake Hood Seaplane Base does not have an IATA, nor appear in the list of flights and will be discarded
                if not iata:
                    continue # skip to next entry

                # handle exceptions or outliers
                if iata in ['DCA', 'IAD']: # DC needs to be manually handled
                    state = 'DC'
                    city = 'WASHINGTON DC'
                elif state == "AK":
                    # Deadhorse is not listed in the city_counties file for some reason
                    if iata == "SCC":
                        my_fips = '2189'
                        ##################
                        associate_ids({"uid": my_fips, "fips": my_fips, "role": role, "size": None, "enplanements": enplanements}) 
                        #fips_lookup[my_fips] = { "code": None, "size": None }
                    elif iata == "SIT":
                        my_fips = '2220'
                        ######################
                        associate_ids({"uid": my_fips, "fips": my_fips, "role": role, "size": None, "enplanements": enplanements}) 
                        #fips_lookup[my_fips] = { "code": None, "size": None }
                    continue
                elif state == "KY":
                    if iata == "CVG":
                        # principal city and airport are in different states
                        test_msa = principal_cities.loc[ principal_cities["Principal City Name"] == 'CINCINNATI' ]
                elif state == "MN":
                    if iata == "MSP":
                        # principal city has unusual name entry
                        test_msa = principal_cities.loc[ principal_cities["Principal City Name"] == 'MINNEAPOLIS' ]
                elif state == "NJ":
                    # "new york" is listed as the primary airport city because ??? 
                    if iata == "EWR":
                        city = "NEWARK"
                elif state == "SC":
                    # airport list omits "island" from the name
                    if iata == "HHH":
                        city = "HILTON HEAD ISLAND"
                elif state == "TN":
                    #  the "tri-cities" are (Bristol, Kingsport, Johnson City) 
                    if iata == "TRI":
                        city = "BRISTOL"
                else:
                    # check to see if this is a metro/micropolitan area
                    test_msa = principal_cities.loc[ (principal_cities["Principal City Name"] == city) & (principal_cities["State"] == state) ]
                
                if not test_msa.empty: # we found a cbsa
                    my_code = test_msa["CBSA Code"].squeeze()
                    my_size = test_msa["Metropolitan/Micropolitan Statistical Area"].squeeze()

                    if my_size.startswith("Metro"):
                        my_size = "METRO"
                    elif my_size.startswith("Micro"):
                        my_size = "MICRO"

                    #associate_ids( {"uid": my_code, "fips": None, "role": role }
                    # associate ALL fips with the CBSA code for jhu lookup
#                    df_test_fips = cbsas.loc[ cbsas["CBSA Code"] == my_code ]
#                    state_fips = df_test_fips["FIPS State Code"].to_list()
#                    county_fips = df_test_fips["FIPS County Code"].to_list()

#                    for (c_state, c_county) in itertools.zip_longest(state_fips, county_fips):
#                        # only the cbsa files use leading zeros - skip them for all other uses
#                        fips_code = (c_state + c_county).lstrip('0')
#                        if fips_code in fips_lookup:
#                            # this fip already exists
#                            # TODO: Task #13 - add enplanements as a sum of all airports within CBSA
#                            continue
#                        fips_lookup[fips_code] = { "code": my_code, "size": my_size } 
#
                # no hits in principal_cities, so no CBSA for this region. Instead lookup fips
                else: 
                    # grab the county for this state/city
                    test_county = city_counties.loc[(city_counties['state'] == state) & (city_counties['city'] == city)]['county']
                    if not test_county.empty: # we found a fips 
                        county = test_county.values[0]
                    else: # truly something has gone wrong
                        breakpoint()
                        raise Exception("we didn't find a county for this city: " + city + " " + state)

                    # now that we have the county for this city, find the fips
                    test_fips = fips.loc[(fips['state'] == state) & (fips['county'] == county)]['fips']
                    if not test_fips.empty:
                        my_fips = test_fips.values[0]

                        associate_ids(my_fips, None)
                        #fips_lookup[my_fips] = { "code": None, "size": None }
                    else:
                        raise Exception("we didn't find cbsa or fips for this county: " county + " " + state )
                     
    return ans

def map_fips_to_cbsa(fip):


