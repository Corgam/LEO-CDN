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


@app.route("/satellite/<satellite_id>/keygroup", methods=["GET"])
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


def run_server():
    print("Coordinator server now running")
    app.run(debug=True, host="172.26.4.1", port=9001, use_reloader=False)
