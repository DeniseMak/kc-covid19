from CsvAccess import KCCsv
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

kcCsvFilename = "data\\kc.csv"

def main():
  data = KCCsv().GetCsvData(kcCsvFilename)

  sortedTuples = sorted(
    ((k,v["NewCases"],v["TotalCases"],v["NewDeaths"],v["TotalDeaths"]) 
     for k,v in data.items()),
    key=lambda x: x[0])
  dates,newCases,totalCases,newDeaths,totalDeaths = zip(*sortedTuples)
  plot(dates,newCases,totalCases,newDeaths,totalDeaths)
  
def sum_to_14_days_ago(i, list):
    s = 0
    if i > 14:
        s= sum(list[:i-14])
    return s

def num_recovered_cases(list):
    # add up the cases per day (new cases) from beginning until current index
    num_recovered = [sum_to_14_days_ago(i, list) for i in range(len(list))]
    return num_recovered

def plot(dates, new_cases, total_cases, new_deaths, total_deaths, log=False):
  plt.plot(new_cases, label="new cases")
  plt.plot(total_cases, label="total cases")
  plt.plot(total_deaths, label="total deaths")

  num_recovered = num_recovered_cases(new_cases)

  total_minus_num_recovered = [total_cases[i] - num_recovered[i] for i in range(len(total_cases))]
  total_minus_num_recovered_and_dead = [total_minus_num_recovered[i] - total_deaths[i] for i in range(len(total_cases))]

  plt.plot(total_minus_num_recovered, 'g--', label="total minus estimated recovered")
  plt.plot(total_minus_num_recovered_and_dead, 'b--',
           label="total minus dead and estimated recovered")
  plt.xticks(np.arange(len(total_cases)), dates, rotation=90)
  plt.legend()
  plt.title("King County COVID-19 cases")

  if log: plt.yscale('log')

  # plt.minorticks_on()

  # Customize the major grid
  plt.grid(color='gray', linestyle='-', linewidth=0.3)
  # Customize the minor grid
  # plt.grid(which='minor', linestyle=':', linewidth=0.3, color='red')

  plt.savefig("covid-cases.png")
  plt.show()

  print("New:{}".format(new_cases))
  print("Total: {}".format(total_cases))
  print('Estimated recovered:{}'.format(num_recovered))
  print("total minus recovered: {}".format(total_minus_num_recovered))
  print('total minus recovered and dead: {}'.format(total_minus_num_recovered_and_dead))
  print("Deaths: {}".format(total_deaths))

if __name__ == "__main__":
    main()
  