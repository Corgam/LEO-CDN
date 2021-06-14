from flask import *
import time
import json
import sys
import requests
import os
import logging
import hashlib
import h3
import toml
import numpy as np
import math
from PyAstronomy import pyasl
from manage_keygroups import *
from satellite import Satellite

app = Flask(__name__)


EARTH_RADIUS = 6371000  # in meter
ALTITUDE = 550  # Orbit Altitude (Km)
semi_major_axis = float(ALTITUDE) * 1000 + EARTH_RADIUS


with open("/config.toml") as f:
    config = toml.load(f)

number_of_planes = config["satellites"]["planes"]
nodes_per_plane = config["satellites"]["satellites_per_plane"]

# Loading node configurations
with open("/info/node.json") as f:
    node_configs = json.load(f)

name = list(node_configs.keys())[0]
ip = node_configs[name]['server']
port = node_configs[name]['sport']
fred = node_configs[name]['fred']
target = f"{node_configs[name]['node']}:{node_configs[name]['nport']}"

#########################
## HTTP Server Methods ##
#########################

# IP:Host/getKeygroups: returns a json of all keygroups the node is in
@app.route('/getKeygroups')
def getKeygroups():
    return jsonify({"keygroups": get_keygroups()})

# IP:host/getLocation: returns the satellite's location (?)
@app.route('/getLocation')
def getLocation():
    return str(satellite.get_current_position)

@app.route('/currentKeygroup')
def addSatellite():
    return str(sat.keygroup)

@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path>')
def catch_all(u_path):
    link = request.headers.get('host') + "/" + u_path
    md5 = hashlib.md5(link.encode()).hexdigest()
    saved = read_file(md5)
    if saved == "":
        # r = requests.get(url=link)
        # set_data("manage", md5, r.text)
        set_data("manage", md5, "0")
        print(f"added new key: {md5}")
        # return r.text
        return "0"
    else:
        print(f"key: {md5} in keygroup manage found: {saved}")
        counter = int(saved.data)
        counter += 1
        saved = str(counter)
        set_data("manage", md5, saved)
        return saved

if __name__ == '__main__':
    STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14
    tmp = math.pow(semi_major_axis, 3) / STD_GRAVITATIONAL_PARAMETER_EARTH
    period = int(2.0 * math.pi * math.sqrt(tmp))
    raan_offsets = [(360 / number_of_planes) * i for i in range(0, number_of_planes)]
    time_offsets = [(period / nodes_per_plane) * i for i in range(0, nodes_per_plane)]
    phase_offset = 0
    phase_offset_increment = (period / nodes_per_plane) / number_of_planes

    # this loop results puts thing in an array in this order:
    # [...8,6,4,2,0,1,3,5,7...]
    # so that the offsets in adjacent planes are similar
    # basically do not want the max and min offset in two adjcent planes
    temp = []
    toggle = False
    for i in range(number_of_planes):
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
            per=period,  # how long the orbit takes in seconds
            a=semi_major_axis,  # if circular orbit, this is same as radius
            e=0,  # generally close to 0 for leo constillations
            Omega=raan,  # right ascention of the ascending node
            w=0.0,  # initial time offset / mean anamoly
            i=53,  # orbit inclination
        )
        list_of_kepler_ellipse.append(ellipse)

    print(len(list_of_kepler_ellipse))
    ellipse = list_of_kepler_ellipse[0]
    # calculate the KE solver time offset
    offset = time_offsets[0] + phase_offsets[0]
    satellite = Satellite(
        name=target,
        server=ip,
        sport=port,
        node=node_configs[name]['node'],
        nport=node_configs[name]['nport'],
        fred=fred,
        kepler_ellipse=ellipse,
        offset=offset,
    )

    try:
        join_managing_keygroups()
    except Exception as e:
        print("failed to join managing keygroup")
        print(e)

    app.run(debug=True, host=ip, port=port)
