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

@app.route("/positions")
def positions():
    satellites_as_list = simulation_with_h3.constellation.get_all_satellites()
    converted_satellites_list = [satellite.__dict__ for satellite in satellites_as_list]
    return jsonify(converted_satellites_list)


@app.route("/best_satellite/<ground_station_id>", methods=["GET"])
def best_satellite(ground_station_id):
    print(f"Got a HTTP request from {str(ground_station_id)}")
    if request.method == "GET":
        if ground_station_id not in simulation_with_h3.ground_stations:
            return "Invalid GST ID"
        else:
            satellite = simulation_with_h3.constellation.get_best_satellite(ground_station_id=ground_station_id)
            return f"{satellite.server}:{satellite.sport}"  # TODO: Change to json or sth like that
    else:
        return "Error - wrong method!"


def run_server():
    print("Coordinator server now running")
    app.run(debug=True, host="172.26.4.1", port=9001, use_reloader=False)
