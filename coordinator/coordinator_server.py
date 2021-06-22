######################
##COORDINATOR SERVER##
######################

from flask import Flask, jsonify, request
import toml
import time 
from simulation_with_h3 import Simulator
from multiprocessing import Process

app = Flask(__name__)


#########################
## HTTP Server Methods ##
#########################


@app.route("/best_satellite/<ground_station_id>", methods=["GET"])
def best_satellite(ground_station_id):
    print(f"Calculating the best satellite to connect to from ground station {str(ground_station_id)}")
    if request.method == "GET":
        if ground_station_id not in simu.ground_stations:
            return "Invalid GST ID"
        else:
            satellite = simu.constellation.get_best_satellite(ground_station_id=ground_station_id)
            return f"{satellite.server}:{satellite.sport}"  # TODO: Change to json or sth like that
    else:
        return "Error - wrong method!"


@app.route("/position/<satellite_id>", methods=["GET"])
def get_satellite_position(satellite_id):
    x, y, z = simu.constellation.get_satellite_position(satellite_id)
    print(f"{satellite_id}: {x} {y} {z}", flush=True)
    response_dict = {
        'x': x,
        'y': y,
        'z': z
    }
    return jsonify(response_dict)


def run_server():
    print("Coordinator server now running")
    app.run(debug=True, host="172.26.4.1", port=9001, use_reloader=False)

if __name__ == '__main__':
    simu = Simulator()
    simu.start()
    run_server()

