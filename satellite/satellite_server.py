from flask import *
import json
import logging
import time
from PyAstronomy import pyasl
from fred_client import FredClient
from satellite import Satellite
from multiprocessing import Process
from lorem_text import lorem
import csv
import toml
from Request import db, Request
import datetime
import sqlite3
# from pathlib import Path
# 
# Path("/db").mkdir(parents=True, exist_ok=True)

# Load the config
with open("./config.toml") as f:
    node_configs = toml.load(f)

# Frequency for sending position queries
frequency = node_configs["satellites"]["position_interval"]
keygroup_layers = node_configs["satellites"]["keygroup_layers"]

# Loading node configurations
with open("/info/node.json") as f:
    node_configs = json.load(f)

name = list(node_configs.keys())[0]
ip = node_configs[name]["server"]
port = node_configs[name]["sport"]
fred = node_configs[name]["fred"]
target = f"{node_configs[name]['node']}:{node_configs[name]['nport']}"
db_server = node_configs[name]['db']

# Loading node configurations
with open("/info/nodes.json") as f:
    node_configs = json.load(f)

nodes = [key for key in node_configs.keys()]

logging.basicConfig(filename='/logs/' + name + '_server.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(f'{name}_server')

files_csv = open('./files.csv', "r")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:123@{db_server}/leo_cdn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.app = app
db.init_app(app)
db.create_all()
db.session.commit()

#########################
## Internal functions  ##
#########################


def join_managing_keygroups():
    try_joining = False
    try:
        response = fred_client.create_keygroup("manage")
        if response.status != 0:
            response = fred_client.add_replica_node_to_keygroup("manage")
            if response.status == 0:
                append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
            else:
                logger.info(f"Couldn't create nor join manage")
        else:
            fred_client.set_data("manage", "addresses", json.dumps(
                ["http://" + ip + ":" + str(port) + "/"]))
    except Exception as e:
        try:
            response = fred_client.add_replica_node_to_keygroup("manage")
            if response.status == 0:
                append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
            else:
                logger.info(f"Couldn't create nor join manage")
        except Exception as e:
            logger.info(f"Couldn't create nor join manage")
            


def append_data(keygroup, key, entry):
    response = fred_client.read_file_from_node(keygroup, key)
    if response.status != 0:
        cur_data = []
        cur_data.append(entry)
        fred_client.set_data(keygroup, key, json.dumps(cur_data))
    else:
        cur_data = json.loads(response.data)
        cur_data.append(entry)
        fred_client.set_data(keygroup, key, json.dumps(cur_data))
    return json.dumps(cur_data)
    # return response

def position_query():
    while(True):
        satellite.check_keygroup()
        time.sleep(frequency)

def get_paragraph_length(file_id):
    reader = csv.reader(files_csv)
    for line in reader:
        if line[0] == file_id:
            return int(line[1])
    
    # if the file_id is not found
    return 5

#########################
## HTTP Server Methods ##
#########################

# IP:host/getValue/<keygroup>/<key>: returns the value of a given key if possible
@app.route("/getValue/<keygroup>/<key>")
def getValueWithKeygroup(keygroup, key):
    return str(fred_client.read_file_from_node(keygroup, key))


# IP:host/getValue/<key>: goes through all keygroups to find the data
@app.route("/getValue/<key>")
def getValue(key):
    return str(fred_client.read_file(key))


# IP:host/setData/<keygroup>/<key>: sets data to the specified key
@app.route("/setData/<keygroup>/<key>", methods=["POST"])
def setData(keygroup, key):
    data = request.data.decode("UTF-8")
    # TODO maybe can just pass on data
    fred_client.set_data(keygroup, key, data)
    resp = fred_client.read_file_from_node(keygroup, key)
    return str(resp)


# IP:host/appendData/<keygroup>/<key>: appends data to the specified key if it is
# a list
@app.route("/appendData/<keygroup>/<key>", methods=["POST"])
def appendData(keygroup, key):
    entry = request.data.decode("UTF-8")
    try:
        cur_data = append_data(keygroup, key, entry)
    except Exception as e:
        return str(e), 500

    return cur_data, 200


@app.route('/getLocation')
def getLocation():
    return str(satellite.get_current_position())

@app.route('/currentKeygroup')
def addSatellite():
    return " ".join(str(x) for x in fred_client.get_keygroups())

@app.route('/mostPopularFile')
def mostPopularFile():
    date = datetime.datetime.utcnow() - datetime.timedelta(hours = 24)
    top_files = db.engine.execute(
        'select file_id, count(file_id) as req_count ' +
       f'from request where time >= "{date}"' + 
        'group by file_id order by req_count;').all()
    return jsonify({'result': list(reversed([row[0] for row in top_files]))})


@app.route("/", defaults={"u_path": ""})
@app.route("/<path:u_path>")
def catch_all(u_path):
    file_id = u_path
    saved = fred_client.read_file(file_id)
    stat_record = Request(file_id=file_id, time=datetime.datetime.utcnow())
    db.session.add(stat_record)
    db.session.commit()
    if saved == "":
        # r = requests.get(url=link)
        # set_data("manage", md5, r.text)
        paragraph_length = get_paragraph_length(file_id)
        lorem_text = lorem.paragraphs(paragraph_length)
        fred_client.set_data("manage", file_id, lorem_text)
        logger.info(f"added new key: {file_id}")
        # return r.text
        return lorem_text
    else:
        logger.info(f"key was found: {file_id}")
        return saved

if __name__ == "__main__":

    # Loading certificates
    with open("/cert/client.crt", "rb") as f:
        client_crt = f.read()

    with open("/cert/client.key", "rb") as f:
        client_key = f.read()

    with open("/cert/ca.crt", "rb") as f:
        ca_crt = f.read()

    fred_client = FredClient(name, fred, target, client_crt, client_key, ca_crt)

    satellite = Satellite(
        name=name,
        fred_client=fred_client,
				keygroup_layers=keygroup_layers,
    )
    
    join_managing_keygroups()

    simulation = Process(target=position_query)
    simulation.start()

    app.run(debug=True, host=ip, port=port, use_reloader=False)
