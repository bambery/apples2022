import os
import csv
import pendulum
import pandas as pd # this is for my convenience, it's not necessary at this stage

# this script parses through the raw data from jhu and creates weekly counts for USA 
# by fips (col 0). It omits any international data, or US data unassociated with a
# county-based fips (ie prisons, cruise ships)

source_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
dest_dir = "../jhu/weekly_us/"
weekly_input_dir = dest_dir

curr_s = source_dir
curr_d = dest_dir 

# I have chosen start/stop on sunday
# 3-22-2020 is the first date that began recording fips and cases in the usa
start_date = pendulum.from_format("03-22-2020", "MM-DD-YYYY")
end_date = pendulum.from_format("03-13-2022", "MM-DD-YYYY")

def todatestr(pen):
    return pen.format("MM-DD-YYYY")

# if desired, this is where a call to pull fresh data from github would live

def build_weekly_data():
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
                header = next(reader)
                # first row is headers - throwing out for now
                for row in reader:
                    if row[0] and row[1] and row[1] != "Unassigned" and not row[1].startswith("Out of"):
                        try:
                            fips = int(row[0])
                        except:
                            breakpoint()
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

def get_weekly_apples():
    # returns dict in the format: { fips: {'MM-DD-YYYY'-> count } } 
    fips_weekly ={}
    for filename in os.listdir(weekly_input_dir):
        # ignore my vim temp files
        if filename.endswith(".csv"):
            weekly_date = filename.removesuffix('_week.csv')
            fips_weekly[weekly_date] = {}
            with open("../jhu/weekly_us/" + filename) as file:
                reader = csv.reader(file, delimiter=",")
                for row in reader:
                    fips = int(row[0])
                    count = int(row[1])
                    fips_weekly[weekly_date][fips] = count
    return fips_weekly

report = get_weekly_apples()
breakpoint()
