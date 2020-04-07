from datetime import date

def testData():
  startDate = date(2020,3,1)
  dates = [date.fromordinal(startDate.toordinal() + i) for i in range(30)]
  newDeaths = list(range(30))
  totalDeaths = list(range(30,60))
  newCases = list(range(60,90))
  totalCases = list(range(90,120))
  values = ({"NewCases":nc,"TotalCases":tc,"NewDeaths":nd,"TotalDeaths":td}   
            for nc,tc,nd,td in zip(newCases,totalCases,newDeaths,totalDeaths))
  d = dict(zip(dates, values))
  return dates,newCases,totalCases,newDeaths,totalDeaths,d
