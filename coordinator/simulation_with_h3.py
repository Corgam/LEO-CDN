import json
import h3
import matplotlib.pyplot as plt
import numpy as np

import keygroup_passer
from simulation.constellation import Constellation

EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)

semi_major_axis = float(ALTITUDE) * 1000 + EARTH_RADIUS
number_of_planes = 1
nodes_per_plane = 8

last_node = number_of_planes * nodes_per_plane  # for node that creates all keygroups

# Loading node configurations
with open("./nodes.json") as f:
    node_configs = json.load(f)

nodes = [key for key in node_configs.keys()]

print(f"Initialize all keygroups:")
h3_center_address = h3.geo_to_h3(0, 0, 0) # lat, lng, hex resolution
all_keygroup_areas_as_ring = h3.k_ring_distances(h3_center_address, 10)

keygroups_color_codes = dict()

for ring in all_keygroup_areas_as_ring:
    ring = list(ring)  # transform {area1, area2} to a list
    ring_as_dict_for_color_code = {k: v for v, k in enumerate(ring)}
    keygroups_color_codes.update(ring_as_dict_for_color_code)
    for area in ring:
        keygroup_passer.create_keygroup(f"node{last_node}", area)

print(f"[simulation_with_h3]: Initialize simulation")
constellation = Constellation(number_of_planes=number_of_planes,
                              nodes_per_plane=nodes_per_plane,
                              semi_major_axis=semi_major_axis)


def plot_current_state(current_time, all_satellites):
    """
    Plots the position of all satellites.

    Parameters
    ----------
    current_time
    all_satellites

    Returns
    -------

    """
    fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.set_xlim([-6e6, 6e6])
    ax.set_ylim([-6e6, 6e6])
    ax.set_zlim([-6e6, 6e6])

    positions = np.array([s.get_current_position() for s in all_satellites])
    xs = positions[:, 0]
    ys = positions[:, 1]
    zs = positions[:, 2]

    keygroup_values_for_satellites = np.array([keygroups_color_codes[s.keygroup] for s in all_satellites])

    ax.scatter(
        xs,
        ys,
        zs,
        marker="o",
        c=keygroup_values_for_satellites,
        vmin=0,
        vmax=3,
    )

    fig.savefig(f"/output/frames/{current_time}_state.png")


steps = 1000
step_length = 5

# starting from time step 0
for step in range(0, steps):
    next_time = step * step_length

    constellation.update_position(time=next_time)
    print(f"At step {step}. These are the current keygroups each satellite belongs to: ")
    constellation.print_current_keygroups()
    # plot_current_state(next_time, constellation.get_all_satellites())



