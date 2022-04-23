import os
import csv
import pendulum
import pandas as pd

# this script parses through the files in the jhu and removes any lines without
# a fips (col 0) or has other formatting to indicate I am not interested in the data 
# New files are created in the folder /resources/jhu/weekly_us

# format of files:
# 0: fips, 1: county name, 2: state name, 3: country abbreviated, 4: not used, 5: lat, 6: long, 7: confirmed cases, 8: deaths, 9: recovered (not used), 10: active (not used), 11: combined_key, 12: incident rate, 13: case fatality ratio

source_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
dest_dir = "../jhu/weekly_us/"

test_dir = "../jhu/COVID-19/csse_covid_19_data/test/"
test_dest = "../jhu/COVID-19/csse_covid_19_data/test_dest/"

curr_s = source_dir
curr_d = dest_dir 

# I have chosen start/stop on sunday
# 3-22-2020 is the first date that began recording fips and cases in the usa
start_date = pendulum.from_format("10-22-2020", "MM-DD-YYYY")
end_date = pendulum.from_format("03-13-2022", "MM-DD-YYYY")

def todatestr(pen):
    return pen.format("MM-DD-YYYY")

def get_apples():
    # initialize for each week
    day = 1
    week_counts = {}
    curr = start_date
    week_start = start_date 

    keep_going = True
    while (keep_going):
        if (day == 8):
            # output weekly report
            output_file = curr_d + todatestr(week_start) + "_week.csv"
            df = pd.DataFrame.from_dict(week_counts, orient='index')
            df.to_csv(output_file, header=False)

            # reset weekly vars
            week_counts = {}
            day = 1
            week_start = curr

        next_file = curr_s + todatestr(curr) + ".csv"
        if os.path.exists(next_file):
            with open(next_file) as file:
                reader = csv.reader(file, delimiter=",")
                # first row is headers - throwing out for now
                header = next(reader)

                # if fips and "county" name are not blank
                for row in reader:
                    if row[0] and row[1] and row[1] != "Unassigned" and not row[1].startswith("Out of"):
                        try:
                            fips = int(row[0])
                        except:
                            raise Exception("You are trying to read something that has a non-number in the fips column: investigate!") 
                        new_tot = int(week_counts.get( fips, 0 )) + int(row[8])
                        week_counts[ fips ]= new_tot 
                day = day + 1
                curr = curr.add(days=1)
                if (curr > end_date):
                    # probably should write out anything I do have to file, but nah
                    keep_going = False
        else:
            raise Exception("trying to open file that doesn't exist: " + next_file) 
            break
