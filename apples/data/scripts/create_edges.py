import os
import csv
import pendulum
import pandas as pd 

# holy fucking christ python needs to get its shit together
from . import Node

source_file = "../county_adjacency/county-adjacency.csv"

# format of file:
# [0] - county, state name
# [1] - fips
# [2] - name of adjacent county
# [3] - fips of adjacent county

def build_county_adjacency():
    edges = {}

    if os.path.exists(source_file):
        with open(source_file) as file:
            reader = csv.reader(file, delimiter=",")
            header = next(reader)
            for row in reader:
                # the first PR (non-us state entry has fips 72001
                if row[1] and not row[1]=="72001": # if a fips is present as a "self" entry
                    curr = int(row[1])
                    edges[curr] = [] # initialize new entry in edges
                elif row[1] and row[1]=="72001":
                    break # if we've hit PR then we are done
                else: # there is no fips in col 1 and we are in the middle of assigning edges
                    edges[curr].append(row[3])
        breakpoint()                
    else:
        print("didn't find it your file")

build_county_adjacency()
