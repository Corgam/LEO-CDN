######################
##COORDINATOR SERVER##
######################

from flask import Flask, jsonify, request
import toml
import simulation_with_h3

app = Flask(__name__)


#########################
## HTTP Server Methods ##
#########################

@app.route("/positions", methods=["GET"])
def positions():
    satellites_as_list = simulation_with_h3.constellation.get_all_satellites()
    converted_satellites_list = [satellite.__dict__ for satellite in satellites_as_list]
    return jsonify(converted_satellites_list)


@app.route("/best_satellite/<ground_station_id>", methods=["GET"])
def best_satellite(ground_station_id):
    print(f"Calculating the best satellite to connect to from ground station {str(ground_station_id)}")
    if request.method == "GET":
        if ground_station_id not in simulation_with_h3.ground_stations:
            return "Invalid GST ID"
        else:
            satellite = simulation_with_h3.constellation.get_best_satellite(ground_station_id=ground_station_id)
            return f"{satellite.server}:{satellite.sport}"  # TODO: Change to json or sth like that
    else:
        return "Error - wrong method!"


@app.route("/satellite/<satellite_id>", methods=["GET"])
def get_satellite_info(satellite_id):
    """
        {
      "position": { "x": 7689789, "y": 105726, "z": 290480 },
      "active": true,
      "connectedSats": [
        { "shell": 0, "sat": 72 },
        { "shell": 0, "sat": 72 },
        { "shell": 0, "sat": 72 },
        { "shell": 0, "sat": 73 }
      ],
      "connectedgst": [{ "name": "tester" }, { "name": "tester2" }]
    }

    Returns
    -------

    """

    print(f"Received Request to return the information about satellite {satellite_id}")
    x, y, z = simulation_with_h3.constellation.get_satellite_position(satellite_id)
    linked_satellites = simulation_with_h3.constellation.get_linked_satellites(satellite_id)
    connected_ground_stations = simulation_with_h3.constellation.get_connected_ground_stations(satellite_id)
    response_dict = {
        'position': {
            'x': x,
            'y': y,
            'z': z
        },
        'connectedSats': linked_satellites,
        'connectedgst': connected_ground_stations
    }
    return jsonify(response_dict)


@app.route("/satellite/<satellite_id>/linked_satellites", methods=["GET"])
def get_linked_satellites(satellite_id):
    linked_satellites = simulation_with_h3.constellation.get_linked_satellites(satellite_id)
    response_dict = {
        'connectedSats': linked_satellites
    }
    return jsonify(response_dict)


@app.route("/satellite/<satellite_id>/position", methods=["GET"])
def get_satellite_position(satellite_id):
    print(f"Received Request to return the position of satellite {satellite_id}")
    x, y, z = simulation_with_h3.constellation.get_satellite_position(satellite_id)
    response_dict = {
        'x': x,
        'y': y,
        'z': z
    }
    return jsonify(response_dict)


@app.route("satellite/<satellite_id>/keygroup", methods=["GET"])
def get_satellite_keygroup(satellite_id):
    print(f"Received Request to return the keygroup of satellite {satellite_id}")
    keygroup = simulation_with_h3.constellation.get_satellite_keygroup(satellite_id)
    return keygroup


@app.route("/ground_station/<ground_station_id>/position", methods=["GET"])
def get_ground_station_position(ground_station_id):
    print(f"Received Request to return the position of ground station {ground_station_id}")
    x, y, z = simulation_with_h3.constellation.get_ground_station_position(ground_station_id)
    response_dict = {
        'x': x,
        'y': y,
        'z': z
    }
    return jsonify(response_dict)


@app.route("/ground_station/<ground_station_id>", methods=["GET"])
def get_ground_station_info(ground_station_id):
    """
    {
  "position": { "x": 6296904, "y": 752587, "z": 611161 },
  "latitude": 5.504684,
  "longitute": 5.765499,
  "connectedSats": [
    {"sat": 0 },
    {"sat": 72 },
    {"sat": 73 },
    {"sat": 74 },
    {"sat": 258 },
    {"sat": 259 },
    {"sat": 260 },
    {"sat": 77 },
    {"sat": 78 }
  ]
}
    Parameters
    ----------
    ground_station_id

    Returns
    -------

    """
    x, y, z = simulation_with_h3.constellation.get_ground_station_position(ground_station_id)
    lat, lon = simulation_with_h3.constellation.get_ground_station_geo_position(ground_station_id)
    connected_satellites = simulation_with_h3.constellation.get_connected_satellites(ground_station_id)
    response_dict = {
        'position': {
            'x': x,
            'y': y,
            'z': z
        },
        'latitude': lat,
        'longitude': lon,
        'connectedSats': connected_satellites
    }
    return jsonify(response_dict)


def run_server():
    print("Coordinator server now running")
    app.run(debug=True, host="172.26.4.1", port=9001, use_reloader=False)
