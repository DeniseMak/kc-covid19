## Note: currently skips plotting a point for dates that don't have new cases
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
new_deaths = []
total_deaths = []
dates = []
print("starting to parse King County site https://kingcounty.gov/depts/health/news/rss.aspx")
t = time.time()

feed['entries'].reverse()
last_case_total = 0
last_death_total = 0
for entry in feed['entries']:
    date = dateutil.parser.parse(entry['published'])
    if date.year > 2019 and ((date.month >= start_month and date.day >= start_date) or (date.month > start_month + 1)):
        query = getluisresult.getluisresult(entry['summary'])
        if show_output:
            print("{}-{}: {}".format(date.month, date.day, query))
        if 'new-cases' in query :
            new_cases.append(int(query['new-cases']))
            if 'total-cases' in query:
                total_cases.append(int(query['total-cases']))
                last_case_total = int(query['total-cases'])
            else:
                new_case_total = last_case_total + int(query['new-cases'])
                total_cases.append(new_case_total)
                last_case_total = new_case_total
            dates.append( str(date.month) + '-' + str(date.day))
            if 'new-deaths' in query:
                new_deaths.append(int(query['new-deaths']))
                if 'total-deaths' in query:
                    total_deaths.append(int(query['total-deaths']))
                    last_death_total = int(query['total-deaths'])
                else:
                    new_death_total = last_death_total + int(query['new-deaths'])
                    total_deaths.append(new_death_total)
                    last_death_total = new_death_total
            else:
                new_deaths.append(0)
                total_deaths.append(last_death_total)

print("Seconds elapsed:{}".format(time.time()-t))

# todo: This isn't necessary anymore since we're casting to int above
# num_new_cases = [int(s) for s in new_cases]
# num_total_cases = [int(s) for s in total_cases]

plt.plot(new_cases, label="new cases")
plt.plot(total_cases, label="total cases")
plt.plot(total_deaths, label="total deaths")

def sum_to_14_days_ago(i, list):
    s = 0
    if i > 14:
        s= sum(list[:i-14])
    return s

def num_recovered_cases(list):
    # add up the cases per day (new cases) from beginning until current index
    num_recovered = [sum_to_14_days_ago(i, list) for i in range(len(list))]
    return num_recovered

num_recovered = num_recovered_cases(new_cases)

total_minus_num_recovered = [total_cases[i] - num_recovered[i] for i in range(len(total_cases))]
total_minus_num_recovered_and_dead = [total_minus_num_recovered[i] - total_deaths[i] for i in range(len(total_cases))]

plt.plot(total_minus_num_recovered, 'g--', label="total minus estimated recovered")
plt.plot(total_minus_num_recovered_and_dead, 'b--',
         label="total minus dead and estimated recovered")
plt.xticks(np.arange(len(total_cases)), dates, rotation=90)
plt.legend()
plt.title("King County COVID-19 cases")


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