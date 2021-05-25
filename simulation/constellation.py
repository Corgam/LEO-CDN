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

from PyAstronomy import pyasl

from simulation.satellite import *
import keygroup_passer

EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)


# according to wikipedia
STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14
# seconds the earth needs to make one whole rotation
SECONDS_PER_DAY = 60 * 60 * 24
# earth's z axis (eg a vector in the positive z direction)
EARTH_ROTATION_AXIS = [0, 0, 1]  # this means the north pole is on the top and the south pole is on the bottom


class Constellation:

    def __init__(self,
                 number_of_planes,
                 nodes_per_plane,
                 semi_major_axis):
        self.number_of_planes = number_of_planes
        self.nodes_per_plane = nodes_per_plane
        self.semi_major_axis = semi_major_axis
        self.period = self.calculate_orbit_period(semi_major_axis=self.semi_major_axis)
        self.list_of_satellites = list()
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
                new_satellite = Satellite(
                    name=f"satellite_{plane}_{node}",
                    number=(plane * self.nodes_per_plane) + node,
                    kepler_ellipse=ellipse,
                    offset=offset,
                )
                self.list_of_satellites.append(new_satellite)

    def calculate_orbit_period(self, semi_major_axis=0.0):
        """calculates the period of a orbit for Earth

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

    def print_current_position(self):
        """
        Prints the current position of every satellite.
        This position is however without any rotation in case we want to simulate the ground station.
        (For the ground stations we would apply the rotation on the ground stations instead of the satellites.)
        Returns
        -------

        """
        for sat in self.list_of_satellites:
            print(f"{sat.number}: {sat.name}")
            print(sat.get_current_position())

    def print_current_keygroups(self):
        for sat in self.list_of_satellites:
            splitted_satellite_name = sat.name.split("_")

            # 0 is the word "satellite"
            plane = splitted_satellite_name[1]
            node_number = splitted_satellite_name[2]
            print(f"{sat.number}: satellite number {node_number} of plane {plane}")
            print(sat.keygroup)

    def get_all_satellites(self):
        """
        Returns the list of all satellites.
        Returns
        -------

        """
        return self.list_of_satellites


if __name__ == "__main__":
    """
    This was just for testing purposes to check whether the satellites move correctly.
    """
    semi_major_axis = float(ALTITUDE) * 1000 + EARTH_RADIUS
    number_of_planes = 1
    nodes_per_plane = 4
    constellation = Constellation(number_of_planes=number_of_planes,
                                  nodes_per_plane=nodes_per_plane,
                                  semi_major_axis=semi_major_axis)

    print("======== initialized position =======")
    constellation.print_current_position()

    steps = 5
    step_length = 1

    for step in range(1, steps):
        next_time = step * step_length

        constellation.update_position(time=next_time)
        all_satellites = constellation.get_all_satellites()
        print(f"======= updated position {step} =======")
        constellation.print_current_position()
