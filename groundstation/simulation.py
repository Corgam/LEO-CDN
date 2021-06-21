import time
from typing import List
from groundstation.groundstation import GroundStation
import pandas as pd
import sys
import json

gsts_config_file = sys.argv[1]
gst_file_popularities_file = sys.argv[2]

df_gst = pd.read_csv(gsts_config_file)
with open(gst_file_popularities_file) as f:
    gst_file_popularities = json.load(f)

p = 0.1
coordinator_host = "http://172.26.4.1:9001"

gsts: List[GroundStation] = []
for index, gst_config in df_gst.iterrows():
    file_order = gst_file_popularities[str(gst_config.id)]
    gst = GroundStation(
        gst_config.id, file_order, p, gst_config.population, coordinator_host
    )
    gsts += [gst]

while True:
    for gst in gsts:
        gst.send_random_file_requests()
    time.sleep(1)
