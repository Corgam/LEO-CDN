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

import math
import numpy as np
from h3 import h3
from manage_keygroups import *


class Satellite:
    """
    This class holds all the information about a single satellite.
    Kepler Ellipse, offset are needed for our own simulation. For the integration into Celestial these two are not
    needed hence, we do not need to use e.g. update position in Celestial.


    Attributes
    ----------
    name: str
        Name of the satellite as "satellite{id} of node on plane}"
    kepler_ellipse: KeplerEllipse
        The kepler ellipse of this satellite.
    offset: int
        The offset of this satellite
    current_time: int
        The current time of the simulation in seconds.
    x_position: int
        The unrotated x position of the satellite.
    y_position: int
        The unrotated y position of the satellite.
    z_position: int
        The unrotated z position of the satellite.
    keygroup:
        The current keygroup of the satellite.
    host:
        Host of the satellite.
    port:
        Port of the satellite.

    """

    def __init__(self, name, server, sport, node, nport, fred, kepler_ellipse=None, offset=0):
        self.name = name
        self.server = server
        self.sport = sport
        self.node = node
        self.nport = nport
        self.fred = fred
        self.kepler_ellipse = kepler_ellipse
        self.offset = offset
        self.current_time = 0
        current_position = self.kepler_ellipse.xyzPos(self.offset)
        self.x_position = current_position[0]
        self.y_position = current_position[1]
        self.z_position = current_position[2]
        self.keygroup = self.init_keygroup()


    def set_new_position(self, current_time):
        """
        Sets the new position of a satellite.
        It calls xyzPos from PyAstronomy KeplerEllipse. The parameter for this function is the time.
        Therefore, we have to add the current time to the offset (the initial position of the satellite)

        Parameters
        ----------
        current_time : int
            new time to calculate the new position

        Returns
        -------

        """
        self.current_time = current_time

        updated_position = self.kepler_ellipse.xyzPos(current_time + self.offset)
        self.x_position = np.int32(updated_position[0])
        self.y_position = np.int32(updated_position[1])
        self.z_position = np.int32(updated_position[2])

        self.check_keygroup()

    def set_xyz_position(self, x, y, z):
        self.x_position = x
        self.y_position = y
        self.z_position = z

    def get_current_position(self):
        """
        Returns the current position of a satellite but without the rotation

        Returns
        -------
        x_position: int
        y_position: int
        z_position: int
        """
        return self.x_position, self.y_position, self.z_position

    def get_rotation_matrix(self, axis, degrees):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.

        This function is copied from Ben S. Kempton and has not been modified.

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

    def get_current_geo_position(self):
        """
        This formula considers the earth to be an ellipsoid.
        It does not calculate the altitude since we only want to know where the position on earth is.
        Returns
        -------
        lon:
            longitude of the position of the satellite
        lat:
            latitude of the position of the satellite

        """
        seconds_per_day = 60 * 60 * 24
        # earth's z axis (eg a vector in the positive z direction)
        earth_rotation_axis = [0, 0, 1]  # this means the north pole is on the top and the south pole is on the bottom

        if self.current_time == 0 or self.current_time % seconds_per_day == 0:
            degrees_to_rotate = 0
        else:
            # how many degrees from time 0 should the earth rotate?
            degrees_to_rotate = 360.0 / (seconds_per_day / (self.current_time % seconds_per_day))

        # have to -degrees to rotate because the satellites moved too far away from the current
        # keygroup and we cannot move the keygroup position because the satellites determine in
        # which keygroup they belong to
        rotation_matrix = self.get_rotation_matrix(earth_rotation_axis, -degrees_to_rotate)

        current_position = self.get_current_position()
        rotated_position = np.dot(rotation_matrix, current_position)

        rotated_x = rotated_position[0]
        rotated_y = rotated_position[1]
        rotated_z = rotated_position[2]

        radius = 6371000
        lon = np.degrees(np.arctan2(rotated_y, rotated_x))
        lat = np.degrees(np.arcsin(rotated_z / radius))

        return lat, lon

    def init_keygroup(self, hex_resolution=0):
        """
        Sets the satellite in the correct initial keygroup.

        Parameters
        ----------
        hex_resolution: int
            Can be between 0 and 15. Determines the size of the hexagon.

        Returns
        -------

        """
        lat, lon = self.get_current_geo_position()
        keygroup_name = h3.geo_to_h3(lat, lon, hex_resolution)  # is the same as h3 area

        print(f"[satellites.py]: Initializing keygroup {keygroup_name} at node {self.name}...")
        target_node = self.fred

        # status_response = keygroup_passer.create_keygroup(target_node=target_node, keygroup=keygroup_name)

        status_response = add_replica_node_to_keygroup(target_node=target_node, keygroup=keygroup_name)

        if status_response.status == 1 or status_response == 2:
            print(f"Oh no. Something went wrong.")
            print(status_response.message)
        return keygroup_name

    def check_keygroup(self, hex_resolution=0):
        """
        Checks whether the keygroup is still the same.
        If yes it returns 0. Otherwise, it returns the new keygroup_id.

        Parameters
        ----------
        hex_resolution

        Returns
        -------

        """
        lat, lon = self.get_current_geo_position()
        new_keygroup_name = h3.geo_to_h3(lat, lon, hex_resolution)  # is the same as h3 area
        old_keygroup_name = self.keygroup
        if new_keygroup_name == old_keygroup_name:
            return None
        else:
            target_node = self.fred
            print(f"Changing keygroup for {self.name} from {old_keygroup_name} to {new_keygroup_name}...")
            status_response_add = add_replica_node_to_keygroup(target_node=target_node,
                                                                               keygroup=f"{new_keygroup_name}")
            # If adding to a keygroup does not work out create the keygroup.
            print(f"[satellite.py]: Status response: {status_response_add}")
            if status_response_add.status == 1 or status_response_add.status == 2:
                print("Cannot add to keygroup.")
                print(status_response_add.message)

            # Removing satellite from keygroup
            status_response_remove = remove_replica_node_from_keygroup(target_node=target_node,
                                                                                       keygroup=f"{old_keygroup_name}")

            print(f"[satellite.py]: Status response: {status_response_remove}")
            # If the satellite cannot be removed from the keygroup
            if status_response_remove.status == 1:
                print("Cannot remove to keygroup.")
                print(status_response_remove.message)
            self.keygroup = new_keygroup_name
            return new_keygroup_name
