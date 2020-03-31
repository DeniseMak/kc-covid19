import csv
from datetime import date
from itertools import *

kcFilename = "data\kc.csv"
cdcFilename = "data\cdc.csv"

def GetRows(filename):
  with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      dateField = date(*(int(x) for x in row["Date"].split('-')))
      yield (dateField, {k : int(row[k]) for k in row.keys() if k != "Date"})

def GetCsvData(filename):
  data = dict()
  for (k,v) in GetRows(filename):
    data[k] = v
  return data

def CalcPercent(fraction, total):
  # Create a double with only 1 digit past the decimal
  perc = int((fraction * 1000) / total)
  return perc / 10

def PrintState(state, data):
  perc = CalcPercent(data[state], data["USCases"])
  print("{0} cases: {1} {2}%".format(state, data[state], perc))

def ScalePerc(perc):
  # For some reason 0.033 * 100 becomes 3.3000000000000003, so
  # we do a second round
  return round(round(perc,3) * 100, 3)

doubles = [
  (9, "3/17", 5),
  (10, "3/22", 5)]

def PrintDoubles(cases):
  for d in doubles:
    print("Double #{0} {1} ({2} days)".format(*d))
  nextDouble = next(dropwhile(lambda x: x < cases, 
                             (pow(2,p) for p in range(32))))
  print("{0} until next double.".format(nextDouble - cases))

def DiffDir(prev, current):
  diff = current - prev
  direction = "down" if diff < 0 else "up"
  diff = abs(diff)
  return diff,direction

def PrintDelta(prev, current, label):
  deltaFormat = "{0} {1} ({2} {3}, {4}%)" 
  diff,direction = DiffDir(prev,current)
  perc = ScalePerc(diff/prev)  
  print(deltaFormat.format(current, label, direction, diff, perc))
  
def PrintPortionDelta(prevFraction, prevTotal, fraction, total, labelA, labelB):
  portionDeltaFormat = "{0}% of {1} are {2} ({3} {4})"

  currPerc = ScalePerc(fraction/total)
  prevPerc = ScalePerc(prevFraction/prevTotal)
  diff,direction = DiffDir(prevPerc,currPerc)
  diff = round(diff, 3)

  print(portionDeltaFormat.format(currPerc, labelA, labelB, direction, diff))


def Anaylize(today, yesterday):

  def _printDelta(set, key,label):
    PrintDelta(yesterday[set][key], today[set][key], label)

  def _printPortionDelta(fractSet, fractKey, totalSet, totalKey, labelA,labelB):
    PrintPortionDelta(
      yesterday[fractSet][fractKey],
      yesterday[totalSet][totalKey],
      today[fractSet][fractKey],
      today[totalSet][totalKey],
      labelA, labelB)

  print("King County")
  _printDelta("kc", "TotalCases", "cases")
  _printDelta("kc", "TotalDeaths", "deaths")
  print()
  PrintDoubles(today["kc"]["TotalCases"])
  print()
  
  if "cdc" not in today:
    print("No cdc data")
    return
  
  print("WA")
  _printDelta("cdc", "WA", "cases")
  _printPortionDelta("kc", "TotalCases", 
                     "cdc", "WA",
                     "WA cases", "King County")
  print()
  print("NY")
  _printDelta("cdc", "NY", "cases")
#  print("{0}x WA cases ({1} {2}")
  print()
  print("US")
  _printDelta("cdc", "USCases", "cases")
  _printDelta("cdc", "USDeaths", "deaths")
  print()
  _printPortionDelta("kc", "TotalCases",
                     "cdc", "USCases",
                     "US cases", "King County")
  _printPortionDelta("kc", "TotalDeaths",
                     "cdc", "USDeaths",
                     "US deaths", "King County")
  print()
  for s in ["NY","WA"]:
    _printPortionDelta("cdc", s,
                       "cdc", "USCases",
                       "US cases", s)
  print() 

def main():
  kc = GetCsvData(kcFilename)
  cdc = GetCsvData(cdcFilename)

  kcDates = sorted(kc.keys(), reverse=True)
  cdcDate = sorted(cdc.keys(), reverse=True)
  
  calcDate = kcDates[0]
  prevCalcDate = kcDates[1]

  currData = {"kc":kc[calcDate]}
  prevData = {"kc":kc[prevCalcDate]}

  cdcAtDate = cdc.get(calcDate)
  if (cdcAtDate is not None):
    currData["cdc"] = cdcAtDate
    # Previous date is whatever previous day we have cdc data for
    prevData["cdc"] = cdc[cdcDate[cdcDate.index(calcDate) + 1]]

  Anaylize(currData, prevData)

  
#  print("US cases", cdcAtDate["USCases"])
#  print("US deaths", cdcAtDate["USDeaths"])
#  PrintState("WA", cdcAtDate)
#  PrintState("NY", cdcAtDate)


if ( __name__ == "__main__"):
    main()
