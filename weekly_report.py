#!/usr/bin/env python3
# coding: utf-8 

import sys
import os
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
        # Otherwise, subtract `dow` number days to get the first day of that week
        start_date = date - timedelta(dow)

    return start_date

def week_person_hour_epics(data):
    """Group by week and person, hours, number of Notes, and list of notes"""

    aggregation = {
        'Hours':{
            'total_hours':'sum'
        },
        'Notes':{
            'note_count':lambda note: np.unique(note[note != '']).size,
            # 'epics':lambda note: "%s" % ', '.join(np.unique(note[note != ''])),
            'epics_list':lambda note: np.unique(note[note != ''])
        }
    }
    df = data.groupby(['Week','Full Name']).agg(aggregation)
    return df

def person_week_hours(data):
    """return table of people by weeks with hours"""
    aggregation = {
        'Hours':'sum',
    }
    df = data.groupby(['Full Name','Week']).agg(aggregation).reset_index()
    return df.pivot(index='Full Name', columns='Week', values=['Hours'])
    
def person_week_epics(data):
    """return table of people by weeks with epics that week"""
    aggregation = {
        'Notes':lambda note: np.unique(note[note != ''])
    }
    df = data.groupby(['Full Name','Week']).agg(aggregation).reset_index()
    return df.pivot(index='Full Name', columns='Week', values='Notes')

def clean_table(data):
    """remove time off, add week, full name columns, and replace nan in Notes with empty strings"""

    # remove time off tasks (sick, vacation)
    df = data[data[config.TASK_COLUMN].str.contains(config.TIME_OFF) == False]

    # add needed columns
    # df['Week'] = df.apply(lambda row:week_start(row['Date']), axis=1)

    df.loc[:,'Week'] = df.apply(lambda row:week_start(row['Date']), axis=1)

    # df['Full Name'] = df.apply(lambda row: row['First Name']+' '+row['Last Name'], axis=1)
    df.loc[:,'Full Name'] = df.apply(lambda row: row['First Name']+' '+row['Last Name'], axis=1)
    df['Notes'].fillna('', inplace=True)
    return df

if __name__ == "__main__":

    # Turn off annoying warnings
    # https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
    pd.options.mode.chained_assignment = None  # default='warn'

    inputFile = config.DEFAULT_IN_FILE
    reportDir = config.DEFAULT_OUT_DIR

    if len(sys.argv) > 2:
        inputFile = sys.argv[1]
        reportDir = sys.argv[2]
    elif len(sys.argv) > 1:
        inputFile = sys.argv[1]

    df = pd.read_csv(inputFile)
    df = clean_table(df)

    if not os.path.exists(reportDir):
        os.makedirs(reportDir)

    # result = week_person_hour_epics(df)
    result = person_week_hours(df)
    print(result)
    result.to_csv(os.path.join(reportDir, "hours.csv"))

    result = person_week_epics(df)
    print(result)
    result.to_csv(os.path.join(reportDir, "epics.csv"))

    

