from flask import *
import grpc
from proto import client_pb2, client_pb2_grpc
import time
import json
import sys
import requests
import os

app = Flask(__name__)

keygroups = ['manage']

# Loading node configurations
with open("/info/node.json") as f:
    node_configs = json.load(f)

name = list(node_configs.keys())[0]
ip = node_configs[name]['server']
port = node_configs[name]['sport']
target = f"{node_configs[name]['node']}:{node_configs[name]['nport']}"

# Loading node configurations
with open("/info/nodes.json") as f:
    node_configs = json.load(f)

nodes = [key for key in node_configs.keys()]

#########################
##### FRED Methods ######
#########################

# Initializes the keygroup
def init_keygroup(kg):
    print(f"Initializing {kg} at {name}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        try:
            response = stub.CreateKeygroup(
                client_pb2.CreateKeygroupRequest(keygroup=kg, mutable=True)
            )
        except:
            pass
        # Add all nodes to read&write role
        print("Allowing all nodes to read&write")
        for node_n in nodes:
            print(node_n)

            give_user_permissions(node_n, kg, 4)

# Adds data to a keygroup
def set_data(kg, key, value):
    print(f"Adding {key}:{value} to {kg}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        response = stub.Update(
            client_pb2.UpdateRequest(keygroup=kg, id=key, data=value)
        )
        print(response)

# Adds node to the keygroup
def add_node_to_keygroup(kg):
    print(f"Adding {name} to {kg}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        response = stub.AddReplica(
            client_pb2.AddReplicaRequest(keygroup=kg, nodeId=name)
        )
        print(response)

# Removes node from the keygroup
def remove_node_from_keygroup(kg):
    print(f"Removing {name} from {kg}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        response = stub.RemoveReplica(
            client_pb2.RemoveReplicaRequest(keygroup=kg, nodeId=name)
        )
        print(response)

# Reads file
def read_file_from_node(keygroup, file_id):
    try:
        print(f"Reading {file_id=} in {keygroup=} from {name=}...")
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            response = stub.Read(
                client_pb2.ReadRequest(keygroup=keygroup, id=file_id)
            )
            return response
    except:
        # if file does not exist an error is raised
        print(f"doesn't exist on {name}")
        return ""

# Reads file
def read_file(file_id):
    for keygroup in keygroups:
        try:
            print(f"Reading {file_id=} in {keygroup=} from {name=}...")
            with grpc.secure_channel(target, credentials=creds) as channel:
                stub = client_pb2_grpc.ClientStub(channel)
                response = stub.Read(
                    client_pb2.ReadRequest(keygroup=keygroup, id=file_id)
                )
                return str(response)
        except:
            # if file does not exist an error is raised
            continue
    print(f"doesn't exist on {name}")
    return ""

def add_role(user, keygroup, role):
    try:
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            response = stub.AddUser(
                client_pb2.UserRequest(
                    user=user, keygroup=keygroup, role=role)
            )
    except:
        # TODO
        print("Failed to give permissions")

#########################
## Internal functions  ##
#########################


def join_managing_keygroups():
    try_joining = False

    try:
        init_keygroup("manage")
    except Exception as e:
        print('"manage" keygroup already exists. Trying to join...')
        print(e.__doc__)
        print(e.message)
        print("Hello")
        try_joining = True
        pass
    print("Hello")
    if try_joining:
        try:
            add_node_to_keygroup("manage")
        except:
            print('node already part of "manage" keygroup.')
            return
        print('successfully joined "manage" keygroup.')

        grpc_response = read_file_from_node("manage", "addresses")
        addresses = json.loads(grpc_response.data)

        # Try obtaining permissions
        for address in addresses:
            data = {
                'node': name,
                'level': 4
            }
            headers = {'Content-Type': "application/json"}
            response = requests.post(
                url=address + "/addRoles/manage",
                json=data,
                headers=headers
            )
            if response.status_code == 200:
                print("successfully obtained permissions")
                break

    # TODO consider putting protocol in other location
    try:
        append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
    except:
        try:
            set_data("manage", "addresses", json.dumps([
                     "http://" + ip + ":" + str(port) + "/"]))
        except:
            print("Even setting data failed. Something went wrong in the RPC connection")
            raise


def give_user_permissions(user, keygroup, level):
    permissions = []
    if level < 0:
        print("level too low")
        return
    if level >= 0:
        permissions.append("ReadKeyGroup")
    if level >= 1:
        permissions.append("WriteKeyGroup")
    if level >= 2:
        permissions.append("ConfigureReplica")
    if level >= 3:
        permissions.append("ConfigureTrigger")
    if level >= 4:
        permissions.append("ConfigureKeygroups")

    for permission in permissions:
        add_role(user, keygroup, permission)


def append_data(keygroup, key, entry):
    response = read_file_from_node(keygroup, key)

    try:
        cur_data = json.loads(response.data)
        cur_data.append(entry)
    except:
        raise

    set_data(keygroup, key, json.dumps(cur_data))
    return json.dumps(cur_data)

#########################
## HTTP Server Methods ##
#########################

# IP:Host/getKeygroups: returns a json of all keygroups the node is in
@app.route('/getKeygroups')
def getKeygroups():
    return jsonify({"keygroups": keygroups})

# IP:Host/initializeKeygroup: initializes a keygroup with testing data
@app.route('/initializeKeygroup', methods=['POST'])
def initializeKeygroup():
    data = request.data.decode('UTF-8')
    try:
        init_keygroup(data)
        keygroups.append(data)
        return getKeygroups()
    except:
        return 'already exists'

# IP:Host/addKeygroup: adds the node to an existing keygroup
@app.route('/addKeygroup', methods=['POST'])
def addKeygroup():
    data = request.data.decode('UTF-8')
    add_node_to_keygroup(data)
    keygroups.append(data)
    return f'Keygroup added: {data}'

# IP:Host/removeKeygroup: removes the node from a keygroup
@app.route('/removeKeygroup', methods=['POST'])
def deleteKeygroup():
    data = request.data.decode('UTF-8')
    remove_node_from_keygroup(data)
    keygroups.remove(data)
    return f'Keygroup removed: {data}'

# IP:host/getValue/<keygroup>/<key>: returns the value of a given key if possible
@app.route('/getValue/<keygroup>/<key>')
def getValueWithKeygroup(keygroup, key):
    return read_file_from_node(keygroup, key)

# IP:host/getValue/<key>: goes through all keygroups to find the data
@app.route('/getValue/<key>')
def getValue(key):
    return read_file(key)

# IP:host/setData/<keygroup>/<key>: sets data to the specified key
@app.route('/setData/<keygroup>/<key>', methods=['POST'])
def setData(keygroup, key):
    data = request.json
    set_data(keygroup, key, data) # TODO maybe can just pass on data
    resp = read_file_from_node(keygroup, key)
    return str(resp)

# IP:host/appendData/<keygroup>/<key>: appends data to the specified key if it is
# a list
@app.route('/appendData/<keygroup>/<key>', methods=['POST'])
def appendData(keygroup, key):
    entry = request.json
    try:
        cur_data = append_data(keygroup, key, entry)
    except:
        return "Requested key does not hold list data", 500
    
    return cur_data, 200


# IP:host/getLocation: returns the satellite's location (?)
@app.route('/getLocation')
def getLocation():
    positions = read_file_from_node("manage", "positions")
    pos = json.loads(positions.data)
    return str(pos[name])


@app.route('/setLocation', methods=['POST'])
def setLocation():
    data = request.data.decode('UTF-8')
    positions = read_file_from_node("manage", "positions")
    pos = json.loads(positions.data)
    pos[name] = data
    set_data("manage", "positions", json.dumps(pos))
    return str(json.dumps(pos))


@app.route('/positions')
def positions():
    return str(read_file_from_node("manage", "positions"))


@app.route('/addRoles/<keygroup>', methods=['POST'])
def addRoles(keygroup):
    try:
        data = json.loads(request.json)
        node = data['node']
        level = int(data['level'])
    except (ValueError, KeyError, TypeError):
        return 
        """ Please provide JSON body in the following form: 
        {
            "node": <node name>,
            "level": <permission level between 0 and 4 (refer to FreD docs)>
        }
        """, 400
    
    try:
        give_user_permissions(node, keygroup, level)
    except:
        return "Internal Server error", 500
    
    return "Successfully gave the specified user" 
    + node + " permission level " + str(level) + ".", 200


if __name__ == '__main__':
    # Loading certificates
    with open("/cert/client.crt", "rb") as f:
        client_crt = f.read()

    with open("/cert/client.key", "rb") as f:
        client_key = f.read()

    with open("/cert/ca.crt", "rb") as f:
        ca_crt = f.read()

    creds = grpc.ssl_channel_credentials(
        certificate_chain=client_crt,
        private_key=client_key,
        root_certificates=ca_crt,
    )
    exist = False
    
    try:
        join_managing_keygroups()
    except:
        print("failed to join managing keygroup")

    init_pos = {f"{name}": {"x": 1, "y": 2, "z": 3}}
    try:
        set_data("manage", "positions", json.dumps(init_pos))
    except:
        print(f"{name} is not allowed to!")

    app.run(debug=True, host=ip, port=port)
