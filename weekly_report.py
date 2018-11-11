#!/usr/bin/env python3
# coding: utf-8 

import sys
from datetime import timedelta
from dateutil.parser import parse
import pandas as pd
import numpy as np

import config

def week_start(date_str):
    """Find the first/last day of the week for the given day.
    Assuming weeks start on Sunday and end on Saturday.

    Returns a tuple of ``(start_date, end_date)``.

    """
    date = parse(date_str)
    # isocalendar calculates the year, week of the year, and day of the week.
    # dow is Mon = 1, Sat = 6, Sun = 7
    year, week, dow = date.isocalendar()

    # Find the first day of the week.
    if dow == 7:
        # Since we want to start with Sunday, let's test for that condition.
        start_date = date
    else:
        # Otherwise, subtract `dow` number days to get the first day
        start_date = date - timedelta(dow)

    return start_date

if __name__ == "__main__":
    inputFile = config.DEFAULT_IN_FILE
    outputFile = config.DEFAULT_OUT_FILE

    if len(sys.argv) > 2:
        inputFile = sys.argv[1]
        outputFile = sys.argv[2]
    elif len(sys.argv) > 1:
        inputFile = sys.argv[1]
        

    df = pd.read_csv(inputFile)

    # add week, full name columns, and replace nan in Notes with empty strings
    df['Week'] = df.apply(lambda row:week_start(row['Date']), axis=1)
    df['Full Name'] = df.apply(lambda row: row['First Name']+' '+row['Last Name'], axis=1)
    df['Notes'].fillna('', inplace=True)
    
    #group by week and person, hours, number of Notes, and list of notes
    epics_by_week = df.groupby(['Week','Full Name']).agg({
        'Hours':{
            'total_hours':'sum'
        },
        'Notes':{
            'note_count':lambda note: np.unique(note[note != '']).size,
            # 'epics':lambda note: "%s" % ', '.join(np.unique(note[note != ''])),
            'epics_list':lambda note: np.unique(note[note != ''])
        }
    })

    print (epics_by_week)
    print(epics_by_week.to_csv(outputFile))

    

