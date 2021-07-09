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
import csv
from collections import OrderedDict
from lorem_text import lorem
import h3
import logging
import requests
import json
from fred_client import FredClient
import numpy as np
import datetime


class CacheStrategy:
    def update_keygroup(self, new_file_ids:list, old_file_ids:dict) -> dict:
        """Updates the old cache with the new file ids"""
        pass

    def add(self, key, value):
        """Adds a key and value to the cache"""
        pass


class LRU(CacheStrategy):
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.cache = OrderedDict()

    def update_keygroup(self, new_file_ids:list, old_file_ids:dict) -> dict:
        """

        Parameters
        ----------
        new_file_ids: list
            List where each row represents a row of the db table
        old_file_ids: dict
            Files retrieved from the meta data keygroup. Key is the file id and value the req_count

        Returns
        -------
        Updated dict for the meta data keygroup

        """
        if len(old_file_ids) > 0:
            self.cache = OrderedDict(old_file_ids)
        if len(new_file_ids) > 0:
            for row in new_file_ids:
                self.add(row["file_id"], row["req_count"])
        return self.cache

    def add(self, key, value):
        """
        Adds key and value to the keygroup cache.
        Parameters
        ----------
        key
        value

        Returns
        -------

        """
        if key not in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            self.cache.move_to_end(key)

        # if cache is full
        if len(self.cache) > self.capacity:
            # remove first
            self.cache.popitem(last=False)


class LFU(CacheStrategy):
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.cache = dict()

    def update_keygroup(self, new_file_ids:list, old_file_ids:dict) -> dict:
        """

        Parameters
        ----------
        new_file_ids: list
            List where each row represents a row of the db table
        old_file_ids: dict
            Files retrieved from the meta data keygroup. Key is the file id and value the req_count

        Returns
        -------
        Updated dict for the meta data keygroup

        """
        if len(old_file_ids) > 0:
            self.cache = old_file_ids
        if len(new_file_ids) > 0:
            for row in new_file_ids:
                self.add(row["file_id"], row["req_count"])

        # divide req_count by two
        # this will reduce the chance that a value that was popular in the beginning still be popular in the end
        # although nobody requested this file anymore
        if len(self.cache) > 0:
            for k, v in self.cache.items():
                self.cache[k] = int(v / 2)
        if len(list(self.cache.keys())) > self.capacity:
            sorted_cache = sorted(self.cache.items(), key=lambda kv: kv[1], reverse=True)
            self.cache = dict(sorted_cache[:-1])
        return self.cache

    def add(self, key, value):
        """
        Adds key and value to the keygroup cache.
        Parameters
        ----------
        key
        value

        Returns
        -------

        """
        if key not in self.cache:
            self.cache[key] = value
        else:
            old_count = self.cache[key]
            # add old and new count
            self.cache[key] = old_count + value


class Personalised(CacheStrategy):
    def __init__(self, capacity=0, expiry_h=24, threshold=10):
        self.capacity = capacity
        self.expiry_h = expiry_h
        self.threshold = threshold
        self.cache = OrderedDict()

    def clean_up(self):
        """
        Cleans up the current cache (meta data keygroup) according to the expiry.
        Returns
        -------

        """
        if len(self.cache) == 0:
            return
        current_time = datetime.datetime.utcnow() - datetime.timedelta(hours=self.expiry_h)
        for key in self.cache.keys():
            # remove from meta data if file hasn't been accessed for the setted expiry time
            if self.cache[key]["timestamp"] < current_time:
                del self.cache[key] # delete key

    def update_keygroup(self, new_file_ids:list, old_file_ids:dict):
        """
        Parameters
        ----------
        new_file_ids: list
            List where each row represents a row of the db table
        old_file_ids: dict
            Files retrieved from the meta data keygroup. Key is the file id and value the req_count

        Returns
        -------
        Updated dict for the meta data keygroup

        """
        if len(old_file_ids) > 0:
            self.cache = OrderedDict(old_file_ids)
        if len(new_file_ids) > 0:
            for row in new_file_ids:
                if row["req_count"] > self.threshold:
                    self.add(row["file_id"], {"timestamp": datetime.datetime.utcnow()})
        self.clean_up()
        return self.cache

    def add(self, key, value):
        """
        Adds key and value to the keygroup cache.
        Parameters
        ----------
        key
        value

        Returns
        -------

        """
        if key not in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            self.cache.move_to_end(key)

        if self.capacity > 0 & len(self.cache) > self.capacity:
            # remove first
            self.cache.popitem(last=False)


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

    def __init__(self,
                 name,
                 fred_client,
                 keygroup_layers,
                 db,
                 kepler_ellipse=None,
                 offset=0,
                 strategy: CacheStrategy = Personalised()
                 ):
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
        self.strategy = strategy
        self.db = db

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

    def get_all_files(self):
        """
        Get all file ids and their amount for the last 24h of the local satellites.
        Returns
        -------

        """
        date = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        top_files = self.db.engine.execute(
            'select file_id, count(file_id) as req_count ' +
            f'from request where time >= "{date}"' +
            'group by file_id order by req_count desc;').all()
        return [files._asdict() for files in top_files]

    def join_metadata_keygroup(self, keygroup):
        """
        Join the metadata keygroup
        Parameters
        ----------
        keygroup
            Name of metadata keygroup.

        Returns
        -------

        """
        status = 1
        try:
            response = self.fred_client.add_replica_node_to_keygroup(keygroup)
            status = response.status
        except Exception as e:
            status = 1
        if status == 1:
            try:
                response = self.fred_client.create_keygroup(keygroup)
            except:
                return

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
        new_keygroup_names = [h3.geo_to_h3(lat, lon, resolution) for resolution in
                              range(self.keygroup_layers)]  # is the same as h3 are
        joined_keygroups = self.fred_client.get_keygroups()

        # remove all the keygroups that contain the word metadata
        joined_keygroups = [ x for x in joined_keygroups if "metadata" not in x ]
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

                    # try to enter the same keygroup but for meta data
                    # if the other keygroup entering failed this should too
                    self.fred_client.add_replica_node_to_keygroup(new_keygroup_names[x]+"metadata")

                except Exception as e:
                    status = 1
                if status == 1:
                    try:
                        response = self.fred_client.create_keygroup(new_keygroup_names[x])
                        # create meta data keygroup
                        response = self.fred_client.create_keygroup(new_keygroup_names[x]+"metadata")
                    except:
                        continue


        # Get all keygroups of the satellite and check if it needs to be removed
        keygroups = self.fred_client.get_keygroups()
        # remove all the keygroups that contain the word metadata
        keygroups = [x for x in keygroups if "metadata" not in x]
        for kg in keygroups:
            remove = False
            for new_kg in new_keygroup_names:
                if kg != new_kg and kg != "manage":
                    remove = True
                    break
            if remove:
                try:
                    self.logger.info(f"[CHECK KEYGROUP]: getting meta data from {kg}")
                    # get current popular files in the current keygroup
                    current_popular_files = self.fred_client.read_file_from_node(f"{kg}metadata", "popular_files")
                    # update all the popular files in the current keygroup
                    all_files = self.strategy.update_keygroup(self.get_all_files(), current_popular_files)
                    # set popular files of current keygroup
                    # this is just a dictionary with keys = file ids, and values = meta data
                    self.fred_client.set_data(f"{kg}metadata", "popular_files", all_files)
                    # remove satellite from keygroup
                    self.fred_client.remove_replica_node_from_keygroup(kg)
                    self.fred_client.remove_replica_node_from_keygroup(kg+"metadata")
                    # TODO clear out db
                except:
                    continue

        # Prints all keygroups of the satellite in the logger
        keygroups = self.fred_client.get_keygroups()
        self.logger.info(f"The keygroups of {self.name}: " + " ".join(str(x) for x in keygroups))
        self.manage(new_keygroup_names)

    def get_files_to_push_or_remove(self, keygroups:list, files_on_top_layer):
        """

        Parameters
        ----------
        keygroups
            list of neighboring keygroups
        files_on_top_layer:
            current file ids in a list that are stored in the upper layer. If this is emtpy it is a string of size 0.

        Returns
        -------

        """
        if len(files_on_top_layer) == 0:
            files_on_top_layer = []
        all_file_id_occurence = list()
        for kg in keygroups:
            # get all popular files from the neighbors and only save the keys = file ids
            self.logger.info(f"[GET FILES TO PUSH AND REMOVE]: getting meta data from {kg}")
            files = self.fred_client.read_file_from_node(f"{kg}metadata", "popular_files")
            if len(files) > 0:
                all_file_id_occurence.append(list(files.keys()))

        list_of_ids_that_should_be_pushed = []
        if len(all_file_id_occurence) > 0:
            # count how many times each file id occurs
            flatten_file_id_occurence = [file_id for sublist in all_file_id_occurence for file_id in sublist]
            counted_common_file_ids = dict()
            # count how many keygroups contain a certain file if
            for id in flatten_file_id_occurence:
                counted_common_file_ids[id] = counted_common_file_ids.get(id, 0) + 1

            # if more than 4 keygroups have the same file id put it in a list of ids that should be on the top layer
            list_of_ids_that_should_be_pushed = [k for k, v in counted_common_file_ids.items() if v >= 4]
        # files that should be on the top layer but aren't
        list_of_ids_to_push_up = list(set(list_of_ids_that_should_be_pushed) - set(files_on_top_layer))
        # files that are in top layer but should not be there
        list_of_ids_to_remove = list(set(files_on_top_layer) - set(list_of_ids_that_should_be_pushed))

        return list_of_ids_to_push_up, list_of_ids_to_remove

    def add_data_to_kg(self, file_ids:list, keygroup):
        """
        Adds the data to a keygroup.
        Parameters
        ----------
        file_ids
            List of file ids to be added into the keygroup
        keygroup
            Keygroup to add the data into. Should be the top layer keygroup.

        Returns
        -------

        """
        if len(file_ids) == 0:
            return
        files_csv = open('./files.csv', "r")
        reader = csv.reader(files_csv)
        paragraphs = 5
        for file_id in file_ids:
            for line in reader:
                if line[0] == file_id:
                    paragraphs = int(line[1])
            lorem_text = lorem.paragraphs(paragraphs)
            self.fred_client.set_data(keygroup, file_id, lorem_text)
            self.logger.info(f"added new key: {file_id}")

    def remove_data_from_kg(self, file_ids:list, keygroup):
        if len(file_ids) == 0:
            return
        for file_id in file_ids:
            self.fred_client.remove_data(kg=keygroup, file_id=file_id)

    def manage(self, keygroups):
        """
        Runs the whole managing process

        Parameters
        ----------
        keygroups:
            Current keygroups the satellite is inside of except for metadata keygroups.

        Returns
        -------
        """

        # Gets a list of keygroups that has a managing role
        manager_list = self.isManager(keygroups)

        # if the list isn't empty, the satellite is a manager
        if len(manager_list) > 0:
            for manage_keygroup in manager_list:
                # Get neighbouring keygroups
                keygroups_to_manage = list(h3.k_ring_distances(manage_keygroup, 1)[1])
                self.logger.info(f"Inside central kg: {manage_keygroup} - manages: {keygroups_to_manage}")

                # Get responsible satellite for each neighbour
                for neighbour in keygroups_to_manage:
                    # enter all surrounding meta data keygroups
                    self.join_metadata_keygroup(neighbour+"metadata")
                    # responsible_satellite = self.fred_client.get_keygroup_replica(neighbour)
                    # self.logger.info(f"{responsible_satellite} is responsible for the neighbour: {neighbour}")

                # get all keygroup this satellite has to check the popular files of
                keygroups_to_manage.append(manage_keygroup)
                # get current files in the top layer
                files_currently_on_top_layer = self.fred_client.read_file_from_node(f"{manage_keygroup}metadata", "layer0_files")
                files_to_push, files_to_remove = self.get_files_to_push_or_remove(keygroups_to_manage, files_currently_on_top_layer)
                self.logger.info(f"Pushing files up {files_to_push}")
                self.logger.info(f"Remove files {files_to_remove} from top layer")
                # push and remove files to layer 0
                # can we do this differently?
                self.add_data_to_kg(files_to_push, keygroups[0])
                self.remove_data_from_kg(files_to_remove, keygroups[0])
                self.fred_client.set_data(kg=manage_keygroup+"metadata", key="layer0_files", value=files_to_push )

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

        # get the center keygroup of resolution 0
        for x in range(1, self.keygroup_layers):
            # Get the central keygroup for resolution x > 0, depending on keygroup_layers in config.toml
            lower_layer_center = h3.h3_to_center_child(keygroups[0], x)
            # Check if the satellite is inside one the manager keygroup
            for i in range(self.keygroup_layers):
                if keygroups[i] == lower_layer_center:
                    managerList.append(keygroups[i])
        return managerList
