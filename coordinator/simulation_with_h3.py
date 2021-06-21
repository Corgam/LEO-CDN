import toml

from constellation import Constellation

# Read the GSTs file
ground_stations = dict()
with open("./temp/gsts.txt") as f:
    for line in f:
        line = line.replace("\n","")
        id, latitude, longitude, country, numberOfRequests = line.split('|')
        ground_stations[id] = {"latitude": latitude,
                               "longitude": longitude}

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


def init():
    print("[simulation_with_h3]: Initialize simulation")
    global constellation
    constellation = Constellation(number_of_planes=number_of_planes,
                                  nodes_per_plane=nodes_per_plane,
                                  semi_major_axis=semi_major_axis)

    # add ground station to simulation
    for key in ground_stations:
        ground_station_data = ground_stations[key]
        constellation.add_new_ground_station(ground_station_id=key,
                                             lat=float(ground_station_data["latitude"]),
                                             lon=float(ground_station_data["longitude"]))

    print("finish initializing")


def run_simulation():
    # starting from time step 0
    for step in range(0, steps):
        next_time = step * step_length

        constellation.update_position(time=next_time)
        # print(f"At step {step}. These are the current keygroups each satellite belongs to: ")
        # constellation.print_current_keygroups()
