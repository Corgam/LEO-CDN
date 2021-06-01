######################
##COORDINATOR SERVER##
######################

from flask import Flask, jsonify, request

from coordinator import Constellation

app = Flask(__name__)

ground_stations = {
    "gst-0": [1, 2, 3],
    "gst-1": [4, 5, 6],
    "gst-2": [7, 8, 9]
}

number_of_planes = 1
nodes_per_plane = 8
constellation = Constellation(number_of_planes=number_of_planes, nodes_per_plane=nodes_per_plane)

for key in ground_stations:
    position = ground_stations[key]
    constellation.add_new_ground_station_xyz(ground_station_id=key,
                                             x=position[0],
                                             y=position[1],
                                             z=position[2])


#########################
## HTTP Server Methods ##
#########################

@app.route("/positions")
def positions():
    satellites_as_list = constellation.get_all_satellites()
    converted_satellites_list = [satellite.__dict__ for satellite in satellites_as_list]
    return jsonify(converted_satellites_list)


@app.route("/best_satellite/<ground_station_id>", methods=["GET"])
def best_satellite(ground_station_id):
    print(f"Got a HTTP request from {str(ground_station_id)}")
    if request.method == "GET":
        if ground_station_id not in ground_stations:
            return "<p>Invalid GST ID</p>"
        else:
            satellite = constellation.get_best_satellite(ground_station_id=ground_station_id)
            return f"{satellite.server}:{satellite.sport}"  # TODO: Change to json or sth like that
    else:
        return "<p>Error - wrong method!</p>"


def run_server():
    app.run(host="172.26.4.1 ", port=9001)


# Main function
if __name__ == '__main__':
    # app.run(host="172.26.5.1", port=9001)
    run_server()
