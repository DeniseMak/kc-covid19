import csv
from datetime import date
from StateAbbrev import *

def GetCsvData(filename):
  return {k : v for (k,v) in _getRows(filename)}

def GetLastEntry(filename):
  (k,v) = list(_getRows(filename))[-1]
  return {k : v}

def AppendRow(filename, rowDict):
  with open(filename, "a", newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=_fieldnames)
    writer.writerow(rowDict)
    csvfile.close()

_fieldnames = ["Date", "USCases", "USDeaths"] + sorted(state_to_abbrev.values())

def _getRows(filename):
  with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      dateField = date(*(int(x) for x in row["Date"].split('-')))
      yield (dateField, {k : int(row[k]) for k in row.keys() if k != "Date"})
  csvfile.close()

def _getReader():
  pass
def _getWriter():
  pass





