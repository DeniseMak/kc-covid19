import datetime
import json
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from CsvAccess import CdcCsv
from StateAbbrev import *

debug = False
cdcCsvFilePath = "data\cdc.csv"

url = "https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html"
jsonUrl = "https://www.cdc.gov/coronavirus/2019-ncov/map-cases-us.json"

def GetData(url):
  response = requests.get(url)
  if response.status_code != 200:
    print("Reauest failed: ", response.status_code, response.text)
    exit(1)
  return response.text

def GetCasesDeaths():
  page = GetData(url)
  soup = BeautifulSoup(page, "html.parser")

  summaryAnchor = soup.find("a", id="2019coronavirus-summary")
  parent = summaryAnchor.parent
  dataItems = parent.find_all("li")
  results = {}
  for i in dataItems:
    split = i.text.split(":")
    if len(split) != 2:
      continue
    results[split[0].strip()] = split[1].strip()
  cases,deaths = results["Total cases"],results["Total deaths"]
  cases = int(cases.replace(',',''))
  deaths = int(deaths.replace(',',''))
  
  return cases,deaths

def main():
  data = dict()
  data["Date"] = datetime.datetime.now().isoformat().split('T')[0]
  data["USCases"], data["USDeaths"] = GetCasesDeaths()

  print("Total cases:", data["USCases"])
  print("Total deaths:", data["USDeaths"])

  stateData = GetUsStateData()
  data.update(stateData)
  
  for juris in sorted(stateData.keys()):
    print(juris, ":", stateData[juris])

  CdcCsv.AppendRow(cdcCsvFilePath, data)

def GetUsStateData():
  usStatesData = GetData(jsonUrl)

  if (debug):
    with open("rawCdcJson.json", "w", encoding="utf-8") as jsonFile:
      jsonFile.write(usStatesData)
      jsonFile.close()

  usStateData = json.loads(usStatesData)
  usStateData = usStateData["data"] 

  # If there is an issue in case count, we use previous day's count,
  # so load up the previous day's numbers
  prev = next(iter(CdcCsv.GetLastEntry(cdcCsvFilePath).values()))  

  extractJuris = ((GetJurisdiction(row),row) for row in usStateData)
  return {juris : GetCaseCount(row, prev[juris]) 
            for juris,row in extractJuris if juris is not None}

def GetJurisdiction(rowData):
  # If abbreviation for juris doesn't exist, we just return the value
  # This also means that if juris is None, which is can be, we return None
  juris = rowData["Jurisdiction"]
  return state_to_abbrev.get(juris, juris)

def GetCaseCount(rowData, prevCount):
  cases = rowData["Cases Reported"]
  if isinstance(cases,int):
    return cases

  if isinstance(cases,str):
    if cases == "None":
      return 0
           
    # one entry in their data (Northern Marianas) is messed up, so used prev day
    # until they fix
    if " to " in cases:
      return prevCount

  # Means we have a new condition to handle
  raise Exception(
    "Unexpected string value [ {0} ] for key [ {1} ]".format(
      cases, jurisdiction))

if ( __name__ == "__main__"):
    main()

