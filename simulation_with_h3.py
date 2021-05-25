import json
import h3

import keygroup_passer
from simulation.constellation import Constellation

EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)

semi_major_axis = float(ALTITUDE) * 1000 + EARTH_RADIUS
number_of_planes = 3
nodes_per_plane = 4

# Loading node configurations
with open("./nodes.json") as f:
    node_configs = json.load(f)

nodes = [key for key in node_configs.keys()]


print(f"Initialize all keygroups:")
h3_center_address = h3.geo_to_h3(0, 0, 0) # lat, lng, hex resolution
all_keygroup_areas_as_ring = h3.k_ring_distances(h3_center_address, 10)

for ring in all_keygroup_areas_as_ring:
    ring = list(ring)  # transform {area1, area2} to a list
    for area in ring:
        keygroup_passer.create_keygroup("node12", area)

print(f"[simulation_with_h3]: Initialize simulation")
constellation = Constellation(number_of_planes=number_of_planes,
                              nodes_per_plane=nodes_per_plane,
                              semi_major_axis=semi_major_axis)

steps = 100
step_length = 60

for step in range(1, steps + 1):
    next_time = step * step_length

    constellation.update_position(time=next_time)
    print(f"At step {step}. These are the current keygroups each satellite belongs to: ")
    constellation.print_current_keygroups()



