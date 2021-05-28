######################
##COORDINATOR SERVER##
######################

from flask import Flask, jsonify, request
import math

app = Flask(__name__)

#Hardcoded satellites' positions, should use coordinator_client.satellite_pos
satellite_positions = {
    "172.26.8.3:5000": [2, 3, 1],
    "172.26.9.3:5000": [5, 4, 6],
    "172.26.10.3:5000": [8, 7, 9]
}

ground_station_positions = {
    "gst-0": [1, 2, 3],
    "gst-1": [4, 5, 6],
    "gst-2": [7, 8, 9]
}

#########################
## HTTP Server Methods ##
#########################

@app.route("/positions")
def positions():
    return jsonify(satellite_positions)

@app.route("/best_satellite/<ground_station_id>", methods = ["GET"])
def best_satellite(ground_station_id):
    print(f"Got a HTTP request from {str(ground_station_id)}")
    if request.method == "GET":
        if ground_station_id not in ground_station_positions:
            return "<p>Invalid GST ID</p>"
        #coordinator_client.getPositions() Should be called periodically to update
        gst_pos = ground_station_positions[ground_station_id]
        mindist = -1
        for key in satellite_positions:
            sat_pos = satellite_positions[key]
            dist = math.sqrt((gst_pos[0]-sat_pos[0])**2 + (gst_pos[1]-sat_pos[1])**2 + (gst_pos[2]-sat_pos[2])**2)
            if (mindist == -1 or dist < mindist):
                mindist = dist
                minkey = key
        return minkey
    else:
        return "<p>Error - wrong method!</p>"

# Main function
if __name__ == '__main__':
    app.run(host="172.26.5.1",port=9001)
