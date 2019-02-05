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
    """Find the first day of the week for the given day.
    Assuming weeks start on Monday and ends on Sunday.
    """
    date = parse(date_str)
    # isocalendar calculates the year, week of the year, and day of the week.
    # dow is Mon = 1, Sat = 6, Sun = 7
    year, week, dow = date.isocalendar()

    start_date = date - timedelta(dow-1)
    return start_date


def person_week_hours(data):
    """return table of people by weeks with hours"""
    aggregation = {
        'Hours':'sum',
    }
    df = data.groupby(['Full Name','Week']).agg(aggregation).reset_index()
    return df.pivot(index='Full Name', columns='Week', values=['Hours'])

def note_aggregator(note):
    agg = np.unique(note[note != ''])

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
    """return table of people by weeks with missing epics that week"""
    aggregation = {
        'Notes':note_aggregator
    }
    df = data.groupby(['Full Name','Week']).agg(aggregation).reset_index()
    # keep only rows where Note columns are missing for the week
    df = df[df['Notes'].str.contains('missing') == True]
    return df.pivot(index='Full Name', columns='Week', values='Notes')

def clean_table(data):
    """add week, full name columns, and replace NaN in Notes with empty strings"""
    data.loc[:,'Week'] = data.apply(lambda row:week_start(row['Date']), axis=1)
    data.loc[:,'Full Name'] = data.apply(lambda row: row['First Name']+' '+row['Last Name'], axis=1)
    data = data.drop(config.UNUSED_COLUMNS, axis=1)
    data['Notes'].fillna('', inplace=True)
    return data

def work_table(data):
    """keep only work hour entries"""
    df = data[data[config.TASK_COLUMN].str.contains(config.TIME_OFF_PREFIX) == False]
    return df

def sred_table(data):
    """keep only SRED entries"""
    df = data[data[config.PROJECT_COLUMN].str.contains(config.SRED_PREFIX)]
    return df

def update_index(df, index):
    """create index on Full Name, then replace with new Full Name index"""
    df = df.reset_index()
    df.set_index("Full Name")
    return df.set_index("Full Name").reindex(index)

def create_people_index(df):
    """create an index with all of the unique names"""
    people = df['Full Name'].unique()
    people = np.sort(people)
    return pd.Index(people, name="Full Name")

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

    # spew out some stats
    print('Total Hours %d' % df['Hours'].sum())
    print('Total SRED Hours %d' % df['Hours'][df['Project'].str.contains('Engineering R&D')].sum())
    print('Number of people reporting %d' % df['Full Name'].nunique())

    if not os.path.exists(reportDir):
        os.makedirs(reportDir)

    # save cleaned up table
    df.to_csv(os.path.join(reportDir, "clean-report.csv"))

    # create complete people index so we have entries for everyone
    people_index = create_people_index(df)

    workdf = work_table(df)

    sreddf = sred_table(df)

    result = person_week_hours(df)
    result = update_index(result, people_index)
    result.to_csv(os.path.join(reportDir, "total-hours.csv"))

    result = person_week_hours(workdf)
    result = update_index(result, people_index)
    result.to_csv(os.path.join(reportDir, "work-hours.csv"))

    result = person_week_hours(sreddf)
    result = update_index(result, people_index)
    result.to_csv(os.path.join(reportDir, "sred-hours.csv"))

    result = person_week_missing(sreddf)
    result = update_index(result, people_index)
    result.to_csv(os.path.join(reportDir, "missing-epics.csv"))

    result = person_week_epics(sreddf)
    result = update_index(result, people_index)
    print(result)

    # print(result)
    result.to_csv(os.path.join(reportDir, "epics.csv"))

    print('Done writing reports in "%s"' % reportDir)

    

