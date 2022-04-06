import os
import csv
import pendulum
import pandas as pd

# this script parses through the files in the jhu and removes any lines without
# a fips (col 0) or has other formatting to indicate I am not interested in the data 

source_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
dest_dir = "../jhu/weekly_us/"
test_dir = "../jhu/COVID-19/csse_covid_19_data/test/"
test_dest = "../jhu/COVID-19/csse_covid_19_data/test_dest/"

curr_s = source_dir
curr_d = dest_dir 

# I have chosen start/stop on sunday
# 3-22-2020 is the first date that began recording fips and cases in the usa
start_date = pendulum.from_format("03-22-2020", "MM-DD-YYYY")
end_date = pendulum.from_format("03-13-2022", "MM-DD-YYYY")

#test_start_date = pendulum.from_format("01-01-2022", "MM-DD-YYYY")
#test_end_date = pendulum.from_format("01-09-2022", "MM-DD-YYYY")

"""
def clean(input, week_count):
    #tmpFile = dest_dir + str(input)
    #input = source_dir + str(input)

    tmpFile = curr_d + str(input)
    input = curr_s + str(input)

    # must pass newline='' for windows
    with open(input, "r", newline='') as file, 
        reader = csv.reader(file, delimiter=",")
        header = next(reader)
        # first row is headers

#        writer.writerow([header[0], header[8]])
        writer.writerow([header[0], "Apples"])

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

def todatestr(pen):
    return pen.format("MM-DD-YYYY")

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
