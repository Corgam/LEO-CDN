from simulation import constellation
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import keygroup_areas

plt.set_cmap("Dark2")

EARTH_RADIUS = 6371000
# Orbit Altitude (Km)
ALTITUDE = 550
semiMajorAxis = float(ALTITUDE) * 1000 + EARTH_RADIUS
STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14

number_of_planes = 1
nodes_per_plane = 3

period = constellation.calculate_orbit_period(semi_major_axis=semiMajorAxis)
satellites, ellipse = constellation.initialize_position(
    number_of_planes, nodes_per_plane, period
)

steps = 14
step_length = 100

decision_planes = keygroup_areas.define_decision_planes(ellipse)

# Calculate satellite positions
positions = []
for step in range(0, steps):
    next_time = step * step_length

    satellites = constellation.update_position(
        all_satellites=satellites, time=next_time
    )
    current_positions = [s.get_current_position() for s in satellites]
    positions.append(current_positions)

positions = np.array(positions)

# Plot satellite positions
fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

markers = ["o", "x", "^"]

for m, s in zip(markers, range(nodes_per_plane)):
    xs = positions[:, s, 0]
    ys = positions[:, s, 1]
    zs = positions[:, s, 2]

    colors = []

    for p in positions[:, s]:
        colors.append(keygroup_areas.keygroup_area_for_point(p, decision_planes).value)

    ax.scatter(xs, ys, zs, marker=m, c=colors, vmin=0, vmax=3)

fig.savefig("output/constellation.png")
