#!/usr/bin/python

import requests
import time
import json
import csv


url = 'http://localhost:8080/shell/0/'

timepoints = 5
i = 0
while (i < timepoints):
    for j in range(7):
        r = requests.get(url + str(j))
        r = r.json()
        print(r["position"]["x"])

        filename = "satellites_" + str(i) + ".csv"
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
            quotechar=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([r["position"]["x"], r["position"]["y"], r["position"]["z"]])
    i = i + 1
    time.sleep(5)
