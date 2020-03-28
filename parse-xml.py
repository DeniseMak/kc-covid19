## Note: currently skips graphing for dates that don't have both new cases and total case info
import feedparser
import dateutil.parser
import getluisresult
import matplotlib.pyplot as plt
import numpy as np
import time

show_output = True
start_month = 3
start_date = 1
rss_url = "https://kingcounty.gov/depts/health/news/rss.aspx"
t = time.time()
feed = feedparser.parse(rss_url)

new_cases = []
total_cases = []
dates = []
print("starting to parse King County site https://kingcounty.gov/depts/health/news/rss.aspx")
t = time.time()
for entry in feed['entries']:
    date = dateutil.parser.parse(entry['published'])
    if date.year > 2019 and ((date.month >= start_month and date.day >= start_date) or (date.month > start_month + 1)): # todo: add or date.month > 3
        query = getluisresult.getluisresult(entry['summary'])
        if show_output:
            print("{}-{}: {}".format(date.month, date.day, query))
        if 'new-cases' in query and 'total-cases' in query:
            new_cases.append(query['new-cases'])
            total_cases.append(query['total-cases'])
            dates.append( str(date.month) + '-' + str(date.day))
print("Seconds elapsed:{}".format(time.time()-t))

num_new_cases = [int(s) for s in new_cases]
num_total_cases = [int(s) for s in total_cases]

num_new_cases.reverse()
num_total_cases.reverse()
dates.reverse()
plt.plot(num_new_cases, label="new cases")
plt.plot(num_total_cases, label="total cases")
plt.xticks(np.arange(len(num_total_cases)), dates, rotation=90)
plt.legend()
plt.title("King County COVID-19 cases")
plt.grid(color='gray', linestyle='-', linewidth=0.3)
plt.savefig("covid-cases.png")
plt.show()