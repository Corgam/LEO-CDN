from flask import *
import time
import json
import sys
import requests
import os
import logging
import hashlib
from fred_client import FredClient

app = Flask(__name__)

# keygroups = ["manage"] # Keygroups the satellite manages

# Loading node configurations
with open("/info/node.json") as f:
    node_configs = json.load(f)

name = list(node_configs.keys())[0]
ip = node_configs[name]['server']
port = node_configs[name]['sport']
fred = node_configs[name]['fred']
target = f"{node_configs[name]['node']}:{node_configs[name]['nport']}"

# Loading node configurations
with open("/info/nodes.json") as f:
    node_configs = json.load(f)

nodes = [key for key in node_configs.keys()]


#########################
## Internal functions  ##
#########################


def join_managing_keygroups():
    try_joining = False

    success = fred_client.init_keygroup("manage")
    if not success:
        print('"manage" keygroup already exists. Trying to join...')
        try:
            fred_client.node_to_keygroup("manage", fred)
            append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
        except:
            print("Was not in the keygroup yet...")
            for node in nodes:
                print("Try to add to keygroup...")
                curr = node_configs[node]
                base_url = "http://" + curr['host'] + ":" + str(curr['port'])
                print(f"Let me talk to {json.dumps(curr)}")
                data = {
                    'node': fred,
                    'satellite' : name,
                    'keygroup': 'manage'
                }
                r = requests.post(url=base_url+"/addToKeygroup/manage", data=json.dumps(data))
                if r.status_code == 200:
                    print("Should be done?")
                    fred_client.node_to_keygroup("manage", fred)
                    append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
                    break
    else:
        fred_client.set_data("manage", "addresses", json.dumps(
            ["http://" + ip + ":" + str(port) + "/"]))
        print("Giving everyone in nodes permission to manage...")
        for x in range(len(nodes)):
                fred_client.add_node_to_keygroup("manage", nodes[x], f"satellite{x}")


def give_user_permissions(user, keygroup, level):
    print(f'Giving {user} permissions for {keygroup} upto lvl {level}...')
    permissions = []
    if level < 0:
        print("level too low")
        return
    if level >= 0:
        permissions.append(0) #ReadKeygroup
    if level >= 1:
        permissions.append(1) #WriteKeyGroup
    if level >= 2:
        permissions.append(2) #ConfigureReplica
    if level >= 3:
        permissions.append(3) #ConfigureTrigger
    if level >= 4:
        permissions.append(4) #ConfigureKeygroups

    for permission in permissions:
        fred_client.add_role(user, keygroup, permission)


def append_data(keygroup, key, entry):
    response = fred_client.read_file_from_node(keygroup, key)
    if not response:
        cur_data = []
        cur_data.append(entry)
        fred_client.set_data(keygroup, key, json.dumps(cur_data))
    else:
        cur_data = json.loads(response.data)
        cur_data.append(entry)
        fred_client.set_data(keygroup, key, json.dumps(cur_data))
    return json.dumps(cur_data)
    # return response

#########################
## HTTP Server Methods ##
#########################

# IP:Host/getKeygroups: returns a json of all keygroups the node is in
@app.route('/getKeygroups')
def getKeygroups():
    return jsonify({"keygroups": fred_client.get_keygroups()})

# IP:Host/initializeKeygroup: initializes a keygroup with testing data
@app.route('/initializeKeygroup', methods=['POST'])
def initializeKeygroup():
    data = request.data.decode('UTF-8')
    if(fred_client.init_keygroup(data)):
        return getKeygroups()
    else:
        return 'already exists'

# IP:Host/addKeygroup: adds the node to an existing keygroup
@app.route('/addToKeygroup', methods=['POST'])
def addKeygroup():
    data = json.loads(request.json)
    if fred_client.add_node_to_keygroup(data['keygroup'], data['fred'], data['satellite']):
        return "Added to keygroup"
    else:
        return "No permission for that", 500

@app.route('/addKeygroup', methods=['POST'])
def addKeygroup2():
    data = json.loads(request.json)
    return fred_client.node_to_keygroup(data['keygroup'], data['fred'])

# IP:Host/removeKeygroup: removes the node from a keygroup
@app.route('/removeKeygroup', methods=['POST'])
def deleteKeygroup():
    data = request.data.decode('UTF-8')
    fred_client.remove_node_from_keygroup(data)
    fred_client.remove_keygroup(data)
    return f'Keygroup removed: {data}'

# IP:host/getValue/<keygroup>/<key>: returns the value of a given key if possible
@app.route('/getValue/<keygroup>/<key>')
def getValueWithKeygroup(keygroup, key):
    return str(fred_client.read_file_from_node(keygroup, key))

# IP:host/getValue/<key>: goes through all keygroups to find the data
@app.route('/getValue/<key>')
def getValue(key):
    return str(fred_client.read_file(key))

# IP:host/setData/<keygroup>/<key>: sets data to the specified key
@app.route('/setData/<keygroup>/<key>', methods=['POST'])
def setData(keygroup, key):
    data = request.data.decode('UTF-8')
    # TODO maybe can just pass on data
    fred_client.set_data(keygroup, key, data)
    resp = fred_client.read_file_from_node(keygroup, key)
    return str(resp)

# IP:host/appendData/<keygroup>/<key>: appends data to the specified key if it is
# a list
@app.route('/appendData/<keygroup>/<key>', methods=['POST'])
def appendData(keygroup, key):
    entry = request.data.decode('UTF-8')
    try:
        cur_data = append_data(keygroup, key, entry)
    except Exception as e:
        return str(e), 500
    
    return cur_data, 200


# IP:host/getLocation: returns the satellite's location (?)
@app.route('/getLocation')
def getLocation():
    positions = fred_client.read_file_from_node("manage", "positions")
    pos = json.loads(positions.data)
    for entry in pos:
        if list(entry.keys())[0] == fred:
            return json.dumps(entry)
    


@app.route('/setLocation', methods=['POST'])
def setLocation():
    data = request.data.decode('UTF-8')
    positions = fred_client.read_file_from_node("manage", "positions")
    pos = json.loads(positions.data)
    pos[name] = data
    fred_client.set_data("manage", "positions", json.dumps(pos))
    return str(json.dumps(pos))


@app.route('/positions')
def positions():
    return str(fred_client.read_file_from_node("manage", "positions"))

@app.route('/addRole/<keygroup>', methods=['POST'])
def addSingleRole(keygroup):
    data = json.loads(request.data)
    node = data['node']
    level = int(data['level'])
    return fred_client.add_role(node, keygroup, level)
        
@app.route('/addRoles/<keygroup>', methods=['POST'])
def addRoles(keygroup):
    try:
        data = json.loads(request.data)
        node = data['node']
        level = int(data['level'])
        give_user_permissions(node, keygroup, level)
        return "Successfully gave the specified user" 
        + node + " permission level " + str(level) + ".", 200
    except Exception as e:

        return str(e), 500
        """ Please provide JSON body in the following form: 
        {
            "node": <node name>,
            "level": <permission level between 0 and 4 (refer to FreD docs)>
        }
        """, 400
    

@app.route('/addSatellite', methods=['POST'])
def addSatellite():
    data = json.loads(request.data.decode('UTF-8'))
    nodes.append(data['node'])
    for kg in fred_client.get_keygroups():
        fred_client.add_node_to_keygroup(kg, data['node'], data['satellite'])
    return str(True)


@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path>')
def catch_all(u_path):
    link = request.headers.get('host') + "/" + u_path
    md5 = hashlib.md5(link.encode()).hexdigest()
    saved = fred_client.read_file(md5)
    if saved == "":
        # r = requests.get(url=link)
        # set_data("manage", md5, r.text)
        fred_client.set_data("manage", md5, "0")
        print(f"added new key: {md5}")
        # return r.text
        return "0"
    else:
        print(f"key: {md5} in keygroup manage found: {saved}")
        counter = int(saved.data)
        counter += 1
        saved = str(counter)
        fred_client.set_data("manage", md5, saved)
        return saved

if __name__ == '__main__':

    # Loading certificates
    with open("/cert/client.crt", "rb") as f:
        client_crt = f.read()

    with open("/cert/client.key", "rb") as f:
        client_key = f.read()

    with open("/cert/ca.crt", "rb") as f:
        ca_crt = f.read()

    fred_client = FredClient(name, target, client_crt, client_key, ca_crt)

    exist = False
    
    try:
        join_managing_keygroups()
    except Exception as e:
        print("failed to join managing keygroup")
        print(e)

    init_pos = {f"{fred}": {"x": 1, "y": 2, "z": 3}}
    
    append_data("manage", "positions", init_pos)

    app.run(debug=True, host=ip, port=port)
