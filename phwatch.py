import requests, datetime

#todo: argparse
acceptable = [7.5, 8.5] #good data interval
interval = 15 #minutes of samples to check (0.33 samples per minute)
threshold = 2 #number of points outside interval to look for
medium = "water quality"
metric = "pH"

def gethalbyname(data, name):
    for d in data:
        if d["name"] == name:
            return d

baseurl = "http://lewaspedia.enge.vt.edu:8080"
r = requests.get(baseurl+"/sites/stroubles1/metricgroups")
d = gethalbyname(r.json, medium)["_embedded"]
tsurl = gethalbyname(d["metrics"], metric)["_links"]["timeseries"]["href"]
timestamp = (datetime.datetime.now()-datetime.timedelta(minutes=15)).isoformat()
ts = requests.get(baseurl+tsurl, params={'since': timestamp})

unacceptable = []
for value, time in ts.json["data"]:
    if value > acceptable[1] or value < acceptable[0]:
        unacceptable.append([value, time])

if len(unacceptable) > threshold:
    print "{0} unacceptable data points! {1}".format(len(unacceptable), unacceptable)
    exit(len(unacceptable))
