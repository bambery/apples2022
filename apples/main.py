#import data.create_fips as cf
import data.process_airports as pa
#import data.process_flights as pf
import data.jhu as jhu

fips = pa.get_fips()
airports = pa.get_airports_cities(fips)

#cf.create_fips()
#pf.get_flights()
