import os
import csv
import pandas as pd

# this script parses through the files in the jhu and removes any lines without
# a fips (col 0) or has other formatting to indicate I am not interested in the data 

source_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
dest_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us_only/"
test_dir = "../jhu/COVID-19/csse_covid_19_data/test/"
test_dest = "../jhu/COVID-19/csse_covid_19_data/test_dest/"

def clean(input):
    #tmpFile = dest_dir + str(input)
    #input = source_dir + str(input)

    tmpFile = test_dest + str(input)
    input = test_dir + str(input)

    # must pass newline='' for windows
    with open(input, "r", newline='') as file, open(tmpFile, "w", newline='') as outFile:
        reader = csv.reader(file, delimiter=",")
        writer = csv.writer(outFile, delimiter=",")
        header = next(reader)
        # first row is headers
        writer.writerow([header[0], header[8]])
        for row in reader: 
            # things I don't care about consistently have no second column value, ie princess cruise, territories
            # also, federal prisons appear to be listed with a blank FIPS, no clue how to count those 
            if row[0] and row[1] and row[1] != "Unassigned" and not row[1].startswith("Out of"):
#                print(row[0], row[1], row[8])
                vals = []
                vals.append(row[0])
                if row[8]:
                    vals.append(row[8])
                else:
                    vals.append(0)
                writer.writerow(vals)
"""
mine = pd.read_csv( test_dir + "01-01-2022-manual.csv")
output = pd.read_csv(test_dest + "01-01-2022.csv")

diff_df = pd.merge(mine, output, how="outer", indicator='Exist')
diff_df = diff_df.loc[diff_df['Exist'] != 'both']
print(diff_df)

"""
#for file in os.listdir(source_dir):
for file in os.listdir(test_dir):
    if file.endswith(".csv"):
        clean(file)
