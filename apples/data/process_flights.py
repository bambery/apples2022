# libraries
import os
import csv
import pandas as pd
#from pandas.compat import StringIO

# internal imports
import shared.utils as utils

resources = utils.get_resource_dir()

file_path_flights = resources.joinpath("flight_routes", "routes.dat")

def get_flights():
    df = pd.read_csv(file_path_flights)
    breakpoint()

