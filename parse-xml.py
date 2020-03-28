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

def sum_to_14_days_ago(i, list):
    s = 0
    if i > 14:
        s= sum(list[:i-14])
    return s

def num_recovered_cases(list):
    # add up the cases per day (new cases) from beginning until current index
    num_recovered = [sum_to_14_days_ago(i, list) for i in range(len(list))]
    return num_recovered

num_recovered = num_recovered_cases(num_new_cases)
print(num_recovered)
num_total_minus_recovered = [num_total_cases[i] - num_recovered[i] for i in range(len(num_total_cases))]

plt.plot(num_total_minus_recovered, 'g--', label="total minus estimated recovered")
plt.xticks(np.arange(len(num_total_cases)), dates, rotation=90)
plt.legend()
plt.title("King County COVID-19 cases")
plt.grid(color='gray', linestyle='-', linewidth=0.3)
plt.savefig("covid-cases.png")
plt.show()