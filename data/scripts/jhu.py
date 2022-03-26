import os
import csv
import pendulum
import pandas as pd

# this script parses through the files in the jhu and removes any lines without
# a fips (col 0) or has other formatting to indicate I am not interested in the data 

source_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/"
dest_dir = "../jhu/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us_only/"
test_dir = "../jhu/COVID-19/csse_covid_19_data/test/"
test_dest = "../jhu/COVID-19/csse_covid_19_data/test_dest/"

curr_s = test_dir
curr_d = test_dest

# I have chosen start/stop on sunday
#start_date = pendulum.from_format("02-02-2020", "MM-DD-YYYY")
#end_date = pendulum.from_format("03-13-2022", "MM-DD-YYYY")

start_date = pendulum.from_format("01-01-2022", "MM-DD-YYYY")
end_date = pendulum.from_format("01-19-2022", "MM-DD-YYYY")

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
        output_file = curr_d + todatestr(week_start) + "_week.csv"
        # output weekly report
        pd.DataFrame(week_counts, index=[0]).to_csv(output_file)
        # reset weekly vars
        week_counts = {}
        #??????????
        raise Exception( weekly_counts)
        breakpoint(pos="eow")
        day = 1
        week_start = curr

    next_file = curr_s + todatestr(curr) + ".csv"
    if os.path.exists(next_file):
        with open(next_file) as file:
            breakpoint(pos="inside week")
            reader = csv.reader(file, delimiter=",")
            header = next(reader)
            # first row is headers - throwing out for now
            for row in reader:
                breakpoint(pos="inside row")
                if row[0] and row[1] and row[1] != "Unassigned" and not row[1].startswith("Out of"):
                    new_tot = week_counts.get( row[0], "0" ) + row[8]
                    week_counts[ row[0] ]= new_tot 
            day = day + 1
            curr = curr.add(days=1)
            if (curr < end_date):
                keep_going = False
    else:
        raise Exception("trying to open file that doesn't exist: " + next_file) 
        break
