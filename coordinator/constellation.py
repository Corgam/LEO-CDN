# This file is part of the uni project "Distributed Systems Prototyping - LEO-CDN" at TU Berlin.
# Copyright (c) 2020 Ben S. Kempton, LEO-CDN project group.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import json
import math
import toml
import numpy as np
from PyAstronomy import pyasl

from satellite.satellite import Satellite

EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)

# according to wikipedia
STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14
# seconds the earth needs to make one whole rotation
SECONDS_PER_DAY = 60 * 60 * 24
# earth's z axis (eg a vector in the positive z direction)
EARTH_ROTATION_AXIS = [0, 0, 1]  # this means the north pole is on the top and the south pole is on the bottom
SEMI_MAJOR_AXIS = float(ALTITUDE) * 1000 + EARTH_RADIUS

class Constellation:
    """
    A class used to contain and manage a satellite constellation
    ...
    Attributes
    ----------
    number_of_planes : int
        the number of planes in the constellation
    nodes_per_plane : int
        the number of satellites per plane
    semi_major_axis : float
        semi major axis of the orbits (radius, if orbits circular)
    period : int
        the period of the orbits in seconds
    list_of_satellites: List[Satellites]
        list of all the satellites in the system.
    current_time : int
        keeps track of the current simulation time

    Methods
    -------
    init_satellites()
        Creates kepler ellipse for each satellites and initialize its position at time 0.
    update_position(time=0)
        Updates all satellites to reflect the new time.
    get_all_satellites()
        Returns all the satellites as a list.
        Each satellite contains information like position (x, y, z) and keygroup.
    print_current_position()
        Prints all the position of each satellite.
    print_current_keygroups()
        Print all satellites and their keygroup they currently belong to.
    """

    def __init__(self,
                 number_of_planes,
                 nodes_per_plane,
                 semi_major_axis=SEMI_MAJOR_AXIS):
        self.number_of_planes = number_of_planes
        self.nodes_per_plane = nodes_per_plane
        self.semi_major_axis = semi_major_axis
        self.period = self.calculate_orbit_period(semi_major_axis=self.semi_major_axis)
        self.list_of_satellites = list()
        self.dict_of_ground_stations = dict()
        self.current_time = 0

        self.init_satellites()

    def init_satellites(self):
        # figure out how many degrees to space right ascending nodes of the planes
        raan_offsets = [(360 / self.number_of_planes) * i for i in range(0, self.number_of_planes)]

        # at which time of the kepler ellipse is the satellite
        # like degree offset (raan_offsets) but as a time in seconds
        time_offsets = [(self.period / self.nodes_per_plane) * i for i in range(0, self.nodes_per_plane)]

        # we offset each plane by a small amount, so they do not "collide"
        # this little algorithm comes up with a list of offset values
        phase_offset = 0
        phase_offset_increment = (self.period / self.nodes_per_plane) / self.number_of_planes
        temp = []
        toggle = False
        # this loop results puts thing in an array in this order:
        # [...8,6,4,2,0,1,3,5,7...]
        # so that the offsets in adjacent planes are similar
        # basically do not want the max and min offset in two adjcent planes
        for i in range(self.number_of_planes):
            if toggle:
                temp.append(phase_offset)
            else:
                temp.insert(0, phase_offset)
                # temp.append(phase_offset)
            toggle = not toggle
            phase_offset = phase_offset + phase_offset_increment

        phase_offsets = temp

        # create kepler ellipse for each degree offset
        list_of_kepler_ellipse = list()
        for raan in raan_offsets:
            ellipse = pyasl.KeplerEllipse(
                per=self.period,  # how long the orbit takes in seconds
                a=self.semi_major_axis,  # if circular orbit, this is same as radius
                e=0,  # generally close to 0 for leo constillations
                Omega=raan,  # right ascention of the ascending node
                w=0.0,  # initial time offset / mean anamoly
                i=53,  # orbit inclination
            )
            list_of_kepler_ellipse.append(ellipse)


        for plane in range(0, self.number_of_planes):
            for node in range(0, self.nodes_per_plane):
                ellipse = list_of_kepler_ellipse[plane]
                # calculate the KE solver time offset
                offset = time_offsets[node] + phase_offsets[plane]
                satellite_number = (plane * self.nodes_per_plane) + node
                with open(f"./temp/satellite{satellite_number}.json") as f:
                    node_configs = json.load(f)
                node_configs = node_configs[f"satellite{satellite_number}"]
                new_satellite = Satellite(
                    name=f"satellite{satellite_number}",
                    server=node_configs["server"],
                    sport=node_configs["sport"],
                    node=node_configs["node"],
                    nport=node_configs["nport"],
                    fred=node_configs["fred"],
                    kepler_ellipse=ellipse,
                    offset=offset,
                )
                self.list_of_satellites.append(new_satellite)

    def add_new_ground_station(self, ground_station_id, lat, lon):
        x, y, z = self.transform_geo_to_xyz(lat, lon)
        self.dict_of_ground_stations[ground_station_id] = {"x": x, "y": y, "z": z}

    def add_new_ground_station_xyz(self, ground_station_id, x, y, z):
        self.dict_of_ground_stations[ground_station_id] = {"x": x, "y": y, "z": z}

    def transform_geo_to_xyz(self, lat, lon):
        """
        Transforms any latitude and longitude to xyz coordinates.
        Taken from Ben S. Kempton.
        Parameters
        ----------
        lat
        lon

        Returns
        -------

        """
        # must convert the lat/long/alt to cartesian coordinates
        radius = EARTH_RADIUS + ALTITUDE
        init_pos = [0, 0, 0]
        latitude = math.radians(lat)
        longitude = math.radians(lon)
        init_pos[0] = radius * math.cos(latitude) * math.cos(longitude)  # x
        init_pos[1] = radius * math.cos(latitude) * math.sin(longitude)   # y
        init_pos[2] = radius * math.sin(latitude)  # z

        # if simulation time is not 0, figure out current position
        if self.current_time == 0 or self.current_time % SECONDS_PER_DAY == 0:
            pos = init_pos

        else:
            degrees_to_rotate = 360.0 / (SECONDS_PER_DAY / (self.current_time % SECONDS_PER_DAY))
            rotation_matrix = self.get_rotation_matrix(EARTH_ROTATION_AXIS, degrees_to_rotate)

            pos = np.dot(rotation_matrix, init_pos)

        x = np.int32(pos[0])
        y = np.int32(pos[1])
        z = np.int32(pos[2])

        return x, y, z

    def get_rotation_matrix(self, axis, degrees):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.

        Taken from Ben S. Kempton.
        Parameters
        ----------
        axis : list[x, y, z]
            a vector defining the rotaion axis
        degrees : float
            The number of degrees to rotate
        """

        theta = math.radians(degrees)
        axis = np.asarray(axis)
        axis = axis / math.sqrt(np.dot(axis, axis))
        a = math.cos(theta / 2.0)
        b, c, d = -axis * math.sin(theta / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

    def calculate_orbit_period(self, semi_major_axis=0.0):
        """
        Calculates the period of a orbit for Earth.

        Parameters
        ----------
        semi_major_axis : float
            semi major axis of the orbit in meters

        Returns
        -------
        Period : int
            the period of the orbit in seconds (rounded to whole seconds)
        """

        tmp = math.pow(semi_major_axis, 3) / STD_GRAVITATIONAL_PARAMETER_EARTH
        return int(2.0 * math.pi * math.sqrt(tmp))

    def update_position(self, time=0):
        """
        Updates the positions of the satellites.

        Parameters
        ----------
        time :
            The new current time.

        """
        self.current_time = time

        for satellite in self.list_of_satellites:
            satellite.set_new_position(self.current_time)

    def get_best_satellite(self, ground_station_id):
        """
        Calculates which of the satellites is the nearest to a ground stations and returns this nearest satellite.
        Parameters
        ----------
        ground_station_id

        Returns
        -------

        """
        ground_station = self.dict_of_ground_stations[ground_station_id]
        shortest_distance = np.inf
        best_satellite = None
        for satellite in self.list_of_satellites:
            x, y, z = satellite.get_current_position()
            # calculate euclidean distance
            distance = int(math.sqrt(
                        math.pow(x - ground_station["x"], 2) +
                        math.pow(y - ground_station["y"], 2) +
                        math.pow(z - ground_station["z"], 2)))
            if distance < shortest_distance:
                # TODO check whether the distance is even allowed
                shortest_distance = distance
                best_satellite = satellite
        return best_satellite

    def print_current_position(self):
        """
        Prints the current position of every satellite.
        This position is however without any rotation in case we want to simulate the ground station.
        (For the ground stations we would apply the rotation on the ground stations instead of the satellites.)
        Returns
        -------

        """
        for sat in self.list_of_satellites:
            print(f"{sat.name}")
            print(sat.get_current_position())

    def print_current_keygroups(self):
        for sat in self.list_of_satellites:
            print(f"{sat.name} is in {sat.keygroup}")

    def get_all_satellites(self):
        """
        Returns the list of all satellites.
        Returns
        -------

        """
        return self.list_of_satellites