import csv
from datetime import date
from StateAbbrev import *

# Classes to use frome this file, defined below
class NytCsv:
  pass
class CdcCsv:
  pass
class KCCsv:
  pass

# Both the NYT csv and the CDC csv (that we create) have the same
# format: a date formated as YYYY-MM-DD, followed by feilds
# so we share the same code for both.
class DateMapCsv:

  def _intFactory(k,v):
    return int(v)

  def __init__(self, dateField, factory=_intFactory):
    self.dateField = dateField
    self.factory = factory

  def GetCsvData(self, filename):
    return {k : v for (k,v) in self._getRows(filename)}

  def GetLastEntry(self, filename):
    item = None
    for item in self._getRows(filename):
      pass
    return {} if item is None else {item[0] : item[1]}

  def _writeCsvData(self, filename, rowDicts, fieldnames):
    with open(filename, "w", newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      for r in rowDicts:
        writer.writerow(r)
      csvfile.close()

  def _appendRow(self, filename, rowDict, fieldnames):
    with open(filename, "a", newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writerow(rowDict)
      csvfile.close()

  def _getRows(self, filename):
    with open(filename, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        dateField = date(*(int(x) for x in row[self.dateField].split('-')))
        yield (dateField, {k : self.factory(k, row[k]) 
                              for k in row.keys() if k != self.dateField})
    csvfile.close()

class NytCsv(DateMapCsv):
  def __init__(self):
    super().__init__("date", NytCsv._rowFactory)

  def _rowFactory(k,v):
    return v if k == "state" else int(v)

  # The NYT data has multiple entries for the same day, one for each
  # state. We want to create a map of date : allStatesDate
  # overload _getRows here, so that GetLastEntry() above will be similar
  # to our cdc csv and return all the data for the most recent day
  # Similary GetCsvData will work too, where without this, it would be
  # writing over the same date keys over and over again
  def _getRows(self, filename):
    currDate = date.min
    day = None
    for k,v in super()._getRows(filename):
      if k < currDate:
        raise Exception("Data set out of order: {0} to {1}".format(
                         currDate, k))     
      if k > currDate:
        if day is not None:
          yield currDate,day
        currDate = k
        day = {}
      
      usState = v["state"]
      del v["state"]
      usState = state_to_abbrev.get(usState, usState)
      day[usState] = v

    if day is not None:
      yield currDate,day

class CdcCsv(DateMapCsv):

  _fieldnames = ["Date", "USCases", "USDeaths"] + sorted(state_to_abbrev.values())
  
  def __init__(self):
    super().__init__(CdcCsv._fieldnames[0])

  def AppendRow(filename, rowDict):
    self._appendRow(filename, rowDict, CdcCsv._fieldnames)

class KCCsv(DateMapCsv):
  _fieldnames = ["Date", "NewCases", "TotalCases", "NewDeaths", "TotalDeaths"]
  
  def __init__(self):
    super().__init__(KCCsv._fieldnames[0])

  def WriteCsvData(self, filename, data):
    dates = sorted(data.keys())
    rowDicts = [dict(data[d], Date=d) for d in dates]
    self._writeCsvData(filename, rowDicts, KCCsv._fieldnames)
