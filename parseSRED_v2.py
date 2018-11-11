# coding: utf-8 

import sys
import csv
from operator import itemgetter

def monthSum(month, personRecordList, workType):
    return int(round(sum( float(y[3]) for y in personRecordList if month in y[0] and y[4] == workType)))
    
def monthSum1(month, personRecordList, workType, description):
    return int(round(sum( float(y[3]) for y in personRecordList \
                                    if month in y[0] and y[4] == workType and description not in y[5])))
    
def personTotal(person, parseList):
    personRecordList = [x for x in parseList if x[2] + ' ' + x[1] == person]
    monthList = ["2017-10", "2017-11", "2017-12", "2018-01", "2018-02", "2018-03", \
                 "2018-04", "2018-05", "2018-06", "2018-07", "2018-08", "2018-09"]

    EngSupport = [monthSum(m, personRecordList, "Engineering Support") for m in monthList]  
    EngGeneral = [monthSum(m, personRecordList, "General") for m in monthList] 
    EngGeneralWOTimeOff = [monthSum1(m, personRecordList, "General", "Time off:") for m in monthList] 

    EngNonSRED = [sum(a) for a in zip(EngSupport, EngGeneralWOTimeOff)]
    EngSREDConnector = [monthSum(m, personRecordList, "Engineering R&D - Connector Functionality Evolution (ENTER TIME TO 2018-09-30)") for m in monthList] 
    EngSREDUniversal = [monthSum(m, personRecordList, "Engineering R&D - Universal Data Transformation Platform (Hub, Sync, Dev, Octane Migrator)  (ENTER TIME TO 2018-09-30)") for m in monthList] 
    EngSREDTools = [monthSum(m, personRecordList, "Engineering R&D - Tools for Combinatorial Feature Complexity  (ENTER TIME TO 2018-09-30)") for m in monthList] 
    EngSREDVisibility = [monthSum(m, personRecordList, "Engineering R&D - Value Stream Management (Viz)") for m in monthList] 

    return [person.upper()] + EngSREDConnector + EngSREDUniversal + EngSREDTools + EngSREDVisibility + EngNonSRED

inputFile = "raw-data/test.csv"
outputFile = "out.csv"

if len(sys.argv) > 2:
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
elif len(sys.argv) > 1:
    inputFile = sys.argv[1]
    outputFile = "out.csv"
    
with open(inputFile, 'r') as f:
    reader = csv.reader(f)
    rawList = list(reader)

# extract relavent fields
columnList = [0, 10, 11, 6, 2, 4]
parseList = [[eachRec[i] for i in columnList] for eachRec in rawList]
del parseList[0]

# find all the uniq people in the list
nameSet = set( l[2] + ' ' + l[1] for l in parseList)

# go through parsed data and accumulate all the monthly data for each individual
yearlyHoursList = [personTotal(name, parseList) for name in nameSet]
yearlyHoursList = sorted(yearlyHoursList, key=itemgetter(0))
for personList in yearlyHoursList:
    print(", ".join( str(e) for e in personList))

    

