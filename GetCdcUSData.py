import json
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

url = "https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html"
jsonUrl = "https://www.cdc.gov/coronavirus/2019-ncov/map-cases-us.json"

def GetData(url):
  response = requests.get(url)
  if response.status_code != 200:
    print("Reauest failed: ", response.status_code, response.text)
    exit(1)
  return response.text
  
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

print("Total cases:", results["Total cases"])
print("Total deaths:", results["Total deaths"])

stateData = GetData(jsonUrl)
stateData = json.loads(stateData)
stateData = stateData["data"]
for s in stateData:
  jurisdiction = s["Jurisdiction"]
  if jurisdiction is None:
    continue
  print(s["Jurisdiction"], ":", s["Cases Reported"])



