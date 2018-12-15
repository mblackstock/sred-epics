#!/usr/bin/env python3
# coding: utf-8 

import sys
import os
from datetime import timedelta
from dateutil.parser import parse
import pandas as pd
import numpy as np
import math

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

def note_aggregator(note):
    agg = np.unique(note[note != ''])
    isNan = False
    try:
        isNan = math.isnan(note)
    except:
        isNan = False

    if isNan:
        return 'None'

    epics = ','.join(agg)
    if epics =='':
        epics='missing'
    return epics

def person_week_epics(data):
    """return table of people by weeks with epics that week"""
    aggregation = {
        'Notes':note_aggregator
    }
    df = data.groupby(['Full Name','Week']).agg(aggregation).reset_index()
    return df.pivot(index='Full Name', columns='Week', values='Notes')

def person_week_missing(data):
    """return table of people by weeks with epics that week"""
    aggregation = {
        'Notes':note_aggregator
    }
    df = data.groupby(['Full Name','Week']).agg(aggregation).reset_index()
    # keep only Note columns that are empty
    df = df[df['Notes'].str.contains('missing') == True]
    return df.pivot(index='Full Name', columns='Week', values='Notes')

def clean_table(data):
    """add week, full name columns, and replace NaN in Notes with empty strings"""
    data.loc[:,'Week'] = data.apply(lambda row:week_start(row['Date']), axis=1)
    data.loc[:,'Full Name'] = data.apply(lambda row: row['First Name']+' '+row['Last Name'], axis=1)
    data['Notes'].fillna('', inplace=True)
    return data

def work_table(data):
    """keep only non-time off entries"""
    df = data[data[config.TASK_COLUMN].str.contains(config.TIME_OFF_PREFIX) == False]
    # df = data.copy()
    # mask = df[config.TASK_COLUMN].str.contains(config.TIME_OFF_PREFIX)
    # df.loc[mask,'Hours'] = 0
    return df

def sred_table(data):
    """keep only SRED entries"""
    df = data[data[config.PROJECT_COLUMN].str.contains(config.SRED_PREFIX)]
    # df = data.copy()
    # mask = df[config.PROJECT_COLUMN].str.contains(config.SRED_PREFIX) == False
    # df.loc[mask,'Hours'] = 0
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

    result = person_week_hours(df)
    print(result)
    result.to_csv(os.path.join(reportDir, "total-hours.csv"))

    result = person_week_hours(work_table(df))
    print(result)
    result.to_csv(os.path.join(reportDir, "work-hours.csv"))

    result = person_week_hours(sred_table(df))
    print(result)
    result.to_csv(os.path.join(reportDir, "sred-hours.csv"))

    result = person_week_missing(sred_table(df))
    print(result)
    result.to_csv(os.path.join(reportDir, "missing-epics.csv"))

    result = person_week_epics(sred_table(df))
    print(result)
    result.to_csv(os.path.join(reportDir, "epics.csv"))

    

