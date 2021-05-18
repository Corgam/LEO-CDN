from simulation import constellation
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import keygroup_areas
import keygroup_passer

plt.set_cmap("Dark2")

EARTH_RADIUS = 6371000
# Orbit Altitude (Km)
ALTITUDE = 550
semiMajorAxis = float(ALTITUDE) * 1000 + EARTH_RADIUS
STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14

number_of_planes = 1
nodes_per_plane = 8

period = constellation.calculate_orbit_period(semi_major_axis=semiMajorAxis)
satellites, ellipse = constellation.initialize_position(
    number_of_planes, nodes_per_plane, period
)
decision_planes = keygroup_areas.define_decision_planes(ellipse)

current_time = 0
step_length = 60

steps = 100
current_steps = 0

current_positions = [s.get_current_position() for s in satellites]
keygroups_for_satellites = [
    keygroup_areas.keygroup_area_for_point(p, decision_planes)
    for p in current_positions
]


def init_keygroups_for_satellites(keygroups_for_satellites):
    for kga in keygroup_areas.KeygroupAreas:
        keygroup = f"{kga.value}"
        target_node_indices = [
            i for i, e in enumerate(keygroups_for_satellites) if e == kga
        ]
        init_node_ind = target_node_indices[0]
        init_node = keygroup_passer.nodes[init_node_ind]
        print(f"Initializing keygroup {keygroup} at node {init_node}...")
        keygroup_passer.init_keygroup(target_node=init_node, keygroup=keygroup)
        for node_ind in target_node_indices[1:]:
            target_node = keygroup_passer.nodes[node_ind]
            print(f"Adding node {target_node} to keygroup {keygroup}...")
            keygroup_passer.add_node_to_keygroup(
                target_node=target_node, keygroup=keygroup
            )


def update_keygroup_assignments(keygroups_for_satellites, new_keygroups_for_satellites):
    for node_ind, (old_kg, new_kg) in enumerate(
        zip(keygroups_for_satellites, new_keygroups_for_satellites)
    ):
        if old_kg != new_kg:
            target_node = keygroup_passer.nodes[node_ind]
            print(f"Changing keygroup for {target_node} from {old_kg} to {new_kg}...")
            keygroup_passer.add_node_to_keygroup(
                target_node=target_node, keygroup=f"{new_kg.value}"
            )
            keygroup_passer.remove_node_from_keygroup(
                target_node=target_node, keygroup=f"{old_kg.value}"
            )


def calc_orbit_normal_vector(x, y, z):
    xy = y - x
    xz = z - x
    normal_vector = np.cross(xy, xz)
    normal_vector = normal_vector / np.linalg.norm(normal_vector)
    return normal_vector


def plot_keygroup_areas(ax, decision_planes):
    xx, yy = np.meshgrid(
        np.linspace(-1 * 10e6, 1 * 10e6, 100), np.linspace(-0.7 * 10e6, 0.7 * 10e6, 100)
    )

    normal = calc_orbit_normal_vector(
        ellipse.xyzPos(0),
        ellipse.xyzPos(ellipse.per / 4),
        ellipse.xyzPos(ellipse.per / 2),
    )
    d = -(normal @ ellipse.xyzCenter())

    # calculate corresponding z
    z = (-normal[0] * xx - normal[1] * yy - d) * 1.0 / normal[2]
    xs = xx.reshape(-1)
    ys = yy.reshape(-1)
    zs = z.reshape(-1)
    colors = []

    normal0, d0 = decision_planes[0]
    normal1, d1 = decision_planes[1]

    for x, y, z in zip(xs, ys, zs):
        p = np.array((x, y, z))
        h0 = p @ normal0 - d0
        h1 = p @ normal1 - d1

        if h0 >= 0 and h1 >= 0:
            colors.append(1)
        elif h0 < 0 and h1 >= 0:
            colors.append(2)
        elif h0 >= 0 and h1 < 0:
            colors.append(3)
        else:
            colors.append(4)

    ax.scatter(xs, ys, zs, c=colors, alpha=0.02)


def plot_current_state(current_time, positions, keygroups_for_satellites):
    fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

    keygroup_values_for_satellites = [kg.value for kg in keygroups_for_satellites]

    plot_keygroup_areas(ax, decision_planes)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    xs = positions[:, 0]
    ys = positions[:, 1]
    zs = positions[:, 2]

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


init_keygroups_for_satellites(keygroups_for_satellites)

while current_steps < steps:
    current_steps += 1
    print("=============")
    satellites = constellation.update_position(
        all_satellites=satellites, time=current_time
    )
    current_positions = np.array([s.get_current_position() for s in satellites])
    plot_current_state(current_time, current_positions, keygroups_for_satellites)
    new_keygroups_for_satellites = [
        keygroup_areas.keygroup_area_for_point(p, decision_planes)
        for p in current_positions
    ]
    print(
        "Current keygroup assignments:", [kg.value for kg in keygroups_for_satellites]
    )
    print(
        "New keygroup assignments:", [kg.value for kg in new_keygroups_for_satellites]
    )
    update_keygroup_assignments(keygroups_for_satellites, new_keygroups_for_satellites)

    print("Updating keygroup assignments if necessary...")

    keygroups_for_satellites = new_keygroups_for_satellites
    current_time += step_length
    print("=============")
    import time

    time.sleep(0.5)
