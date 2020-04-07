## Note: currently skips plotting a point for dates that don't have new cases
from collections import namedtuple
from CsvAccess import KCCsv
from datetime import date
from datetime import datetime
import dateutil.parser
import feedparser
import getluisresult
import time

show_output = False

# By default we collect only what is missing in the csv file. 
# Set to True to collect everything
collect_all = True

# 3/1 has 2 entries indicating deaths, which we don't expect, so start
# on 3/2
start_month = 3
start_day = 2
start_date = date(2020, start_month, start_day)

rss_url = "https://kingcounty.gov/depts/health/news/rss.aspx"

kcCsvFilename = "data\\kc.csv"

Record = namedtuple("Record", "new_cases total_cases new_deaths total_deaths")

def main():
    feed = feedparser.parse(rss_url)

    records = {}

    if not collect_all:
        records = LoadExistingRecords()

    # Keep track of query objects based on date, so we can 
    # inspect ones that we failed to extract from
    date_query = {}

    print("starting to parse King County site https://kingcounty.gov/depts/health/news/rss.aspx")
    t = time.time()

    last_case_total = 0
    last_death_total = 0
    for entry in reversed(feed['entries']):
        pub_date = dateutil.parser.parse(entry['published'])
        record_date = pub_date.date()

        if record_date < start_date:
            continue

        if record_date in records:
            continue

        query = getluisresult.getluisresult(entry['summary'])
        date_query[record_date] = query
        
        if show_output:
            print("{}: {}".format(record_date.isofromat(), query))

        if 'new-cases' not in query:
            continue
            
        new_cases = int(query['new-cases'])

        if 'total-cases' in query:
            total_cases = int(query['total-cases'])
        else:
            total_cases = last_case_total + new_cases

        last_case_total = total_cases

        if 'new-deaths' in query:
            new_deaths = int(query['new-deaths'])
            
            if 'total-deaths' in query:
                total_deaths = int(query['total-deaths'])
            else:
                total_deaths = last_death_total + new_deaths
        else:
            new_deaths = 0
            total_deaths = last_death_total

        last_death_total = total_deaths
        
        records[record_date] = Record(new_cases, total_cases,
                                      new_deaths, total_deaths)

    print("Seconds elapsed:{}".format(time.time()-t))

    CheckForParseIssues(records, date_query)

    KCCsv().WriteCsvData(kcCsvFilename, 
        {k:recordToCsvDict(v) for k,v in records.items()})

def CheckForParseIssues(records, date_query):
    dates = sorted(records.keys())
    missing = findMissingDates(dates[0], dates[-1], dates)

    for d in missing:
      print("Missing {} : {}".format(
          d.isoformat(), 
          date_query.get(d, "No query results")))

def findMissingDates(start, end, dates):
    dateSet = set(d.toordinal() for d in dates)
    startOrd = start.toordinal()
    endOrd = end.toordinal()
    
    return [date.fromordinal(ord) for ord in range(startOrd,endOrd+1)
              if ord not in dateSet]

def csvDictToRecord(d):
    fieldNames = ("NewCases","TotalCases","NewDeaths","TotalDeaths")
    return Record(*(d[k] for k in fieldNames))

def recordToCsvDict(r):
    fieldNames = ("NewCases","TotalCases","NewDeaths","TotalDeaths")
    return dict(zip(fieldNames, r))

def LoadExistingRecords():

    try:
      data = (KCCsv().GetCsvData(kcCsvFilename))
    except:
      return {}

    return {k:csvDictToRecord(v) for k,v in data.items()}

if __name__ == "__main__":
    main()
