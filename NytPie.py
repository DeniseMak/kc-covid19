import matplotlib.pyplot as plt
import sys
from CsvAccess import NytCsv

# NYT covid-data github
# https://github.com/nytimes/covid-19-data.git

# Path to a local copy of the csv, can be specified as first command line param
defaultNytCsvFilePath = "\\NytCovid19\\covid-19-data\\us-states.csv"

def main():
  nytCsvFilePath = defaultNytCsvFilePath
  if len(sys.argv) > 1:
    nytCsvFilePath = sys.argv[1]

  PlotMostRecent(nytCsvFilePath)

  plt.show()

def PlotAll(nytCsvFilePath):
  nytCsv = NytCsv()

  history = nytCsv.GetCsvData(nytCsvFilePath)
  dates = sorted(history.keys())
  # This doesn't work; it creates a mess, curious how to
  # create multiple views that you could cycle through with the 
  # arrows
  for d in dates:
    PlotPie(history[d])

def PlotMostRecent(nytCsvFilePath):
  nytCsv = NytCsv()

  # Get the most recent data, just get the value part of the single 
  # entry in the last { date : stateDataDict } dictionary
  mostRecent = next(iter(nytCsv.GetLastEntry(nytCsvFilePath).values()))  

  PlotPie(mostRecent)

def PlotPie(caseMap):
  
  # Remove the extra fields, map state to just cases
  caseMap = {k : caseMap[k]["cases"] for k in caseMap}
  
  totalCases = sum(caseMap.values())

  percentages = ((k,v*100/totalCases) for k,v in caseMap.items())
  percentages = sorted(percentages, reverse=True, key=lambda x: x[1])
  top = percentages[:10]
  othersSum = sum(i[1] for i in percentages[10:])
  top.append(("others", othersSum))

  labels,sizes = zip(*top)
  colors = rgbColors

  pieData = plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, shadow=True, startangle=140)
  plt.axis('equal')

  
def rgbToHtmlStr(r,g,b):
  return "#{:02x}{:02x}{:02x}".format(r,g,b)

rgbColors= [
  (0,192,255),
  (0,255,192),
  (192,0,255),
  (192,255,0),
  (255,0,192),
  (255,192,0),
  (192,192,255),
  (192,255,192),
  (255,192,192),
  (192,255,255),
  (255,192,255),
  (255,192,255)
]

rgbColors = [rgbToHtmlStr(*x) for x in rgbColors] 

if __name__ == "__main__":
  main()
