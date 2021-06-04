import json
import h3
import matplotlib.pyplot as plt
import numpy as np
import toml

from satellite.manage_keygroups import *
from constellation import Constellation

global constellation

print("simulation running")

ground_stations = {
    "gst-0": [1, 2, 3],
    "gst-1": [4, 5, 6],
    "gst-2": [7, 8, 9]
}

EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)
semi_major_axis = float(ALTITUDE) * 1000 + EARTH_RADIUS

steps = 1000
step_length = 5

# Load the config
with open("./config.toml") as f:
    config = toml.load(f)

# Number of nodes to generate
number_of_planes = config["satellites"]["planes"]
nodes_per_plane = config["satellites"]["satellites_per_plane"]

last_node = number_of_planes * nodes_per_plane  # for node that creates all keygroups

if __name__ == '__main__':
    print(f"Initialize all keygroups:")
    h3_center_address = h3.geo_to_h3(0, 0, 0)  # lat, lng, hex resolution
    all_keygroup_areas_as_ring = h3.k_ring_distances(h3_center_address, 10)

    for ring in all_keygroup_areas_as_ring:
        ring = list(ring)  # transform {area1, area2} to a list
        for area in ring:
            create_keygroup(f"satellite{last_node}", area)

    print(f"[simulation_with_h3]: Initialize simulation")
    constellation = Constellation(number_of_planes=number_of_planes,
                                  nodes_per_plane=nodes_per_plane,
                                  semi_major_axis=semi_major_axis)

    for key in ground_stations:
        position = ground_stations[key]
        constellation.add_new_ground_station_xyz(ground_station_id=key,
                                                 x=position[0],
                                                 y=position[1],
                                                 z=position[2])

    # starting from time step 0
    for step in range(0, steps):
        next_time = step * step_length

        constellation.update_position(time=next_time)
        print(f"At step {step}. These are the current keygroups each satellite belongs to: ")
        constellation.print_current_keygroups()
