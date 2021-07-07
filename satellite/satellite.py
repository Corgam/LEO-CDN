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

import h3
import logging
import requests
import json
from fred_client import FredClient
import numpy as np

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
    fredComm:
        fred functions class
    """

    def __init__(self, name, fred_client, keygroup_layers, kepler_ellipse=None, offset=0):
        logging.basicConfig(filename='/logs/' + name + '_satellite.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
        self.logger = logging.getLogger(f'{name}_satellite')
        self.name = name
        self.fred_client = fred_client
        self.keygroup_layers = keygroup_layers
        self.baseurl = "http://172.26.4.1:9001/position/" + name

    def get_current_position(self):
        """
        Returns the current position of a satellite but without the rotation

        Returns
        -------
        x_position: int
        y_position: int
        z_position: int
        """
        r = requests.get(url=self.baseurl)
        position = json.loads(r.text)
        radius = 6371000
        lon = np.degrees(np.arctan2(position['y'], position['x']))
        lat = np.degrees(np.arcsin(position['z'] / radius))

        return lat, lon

    def check_keygroup(self):
        """
        Checks whether the keygroup is still the same.
        If yes it returns 0. Otherwise, it returns the new keygroup_id.

        Parameters
        ----------
        hex_resolution

        Returns
        -------

        """
        lat, lon = self.get_current_position()
        new_keygroup_names = [h3.geo_to_h3(lat, lon, resolution) for resolution in range(self.keygroup_layers)]  # is the same as h3 are 
        joined_keygroups = self.fred_client.get_keygroups()
        
        # Checks if the new_keygroup_names need to be joined
        needsToJoin = [True for x in range(self.keygroup_layers)]
        for kg in joined_keygroups:
            for x in range(self.keygroup_layers):
                # Checks if the satellite is already inside the keygroup
                if kg == new_keygroup_names[x]:
                    needsToJoin[x] = False
                    break
        
        for x in range(self.keygroup_layers):
            # If the satellite isn't inside the keygroup yet
            if needsToJoin[x]:
                status = 1
                try:
                    response = self.fred_client.add_replica_node_to_keygroup(new_keygroup_names[x])
                    status = response.status
                except Exception as e:
                    status = 1
                if status == 1:
                    try:
                        response = self.fred_client.create_keygroup(new_keygroup_names[x])
                    except:
                        continue

        # Get all keygroups of the satellite and check if it needs to be removed
        keygroups = self.fred_client.get_keygroups()
        for kg in keygroups:
            remove = False
            for new_kg in new_keygroup_names:
                if kg != new_kg and kg != "manage":
                    remove = True
                    break
            if remove:
                try:
                    self.fred_client.remove_replica_node_from_keygroup(kg)
                except:
                    continue

        # Prints all keygroups of the satellite in the logger
        keygroups = self.fred_client.get_keygroups()
        self.logger.info(f"The keygroups of {self.name}: " + " ".join(str(x) for x in keygroups))
        self.manage(new_keygroup_names)

    def manage(self, keygroups):
        """
        Runs the whole managing process

        Parameters
        ----------
        Current keygroups the satellite is inside of

        Returns
        -------
        """

        # Gets a list of keygroups that has a managing role
        manager_list = self.isManager(keygroups)

        # if the list isn't empty, the satellite is a manager
        if len(manager_list) > 0:
            for manage_keygroup in manager_list:
                # Get neighbouring keygroups
                keygroups_to_manage = h3.k_ring_distances(manage_keygroup, 1)[1]
                self.logger.info(f"Inside central kg: {manage_keygroup} - manages: {keygroups_to_manage}")

                # Get responsible satellite for each neighbour
                for neighbour in keygroups_to_manage:
                    responsible_satellite = self.fred_client.get_keygroup_replica(neighbour)
                    self.logger.info(f"{responsible_satellite} is responsible for the neighbour: {neighbour}")

    def isManager(self, keygroups):
        """
        Checks whether the satellite is a manager.

        Parameters
        ----------
        Current keygroups the satellite is inside of

        Returns
        -------
        List of keygroups that the satellite manages
        """
        managerList = []

        # keygoup[0] is the keygroup with resolution 0, get the central position
        center_coordinates = h3.h3_to_geo(keygroups[0])

        for x in range(1, self.keygroup_layers):
            # Get the central keygroup for resolution x > 0, depending on keygroup_layers in config.toml  
            lower_layer_center = h3.geo_to_h3(center_coordinates[0], center_coordinates[1], x)
            # Check if the satellite is inside one the manager keygroup
            for i in range(self.keygroup_layers):
                if keygroups[i] == lower_layer_center:
                    managerList.append(keygroups[i])
        
        return managerList
