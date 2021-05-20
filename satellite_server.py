from flask import *
import grpc
from proto import client_pb2, client_pb2_grpc
import time
import json
import sys

app = Flask(__name__)

keygroups = ['manage']

# Loading node configurations
with open("/info/node.json") as f:
    node_configs = json.load(f)

name = list(node_configs.keys())[0]
ip = node_configs[name]['server']
port = node_configs[name]['sport']
target = f"{node_configs[name]['node']}:{node_configs[name]['nport']}"

#########################
##### FRED Methods ######
#########################

# Initializes the keygroup
def init_keygroup(kg, key, value):
    print(f"Initializing {kg} at {name}...")
    try:
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            response = stub.CreateKeygroup(
                client_pb2.CreateKeygroupRequest(keygroup=kg, mutable=True)
            )
            print(response)
            response = stub.Update(
                client_pb2.UpdateRequest(keygroup=kg, id=key, data=value)
            )
            print(response)
    except Exception as e:
        return

# Adds data to a keygroup
def add_data(kg, key, value):
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
    except Exception as e:
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
        except Exception as e:
            # if file does not exist an error is raised
            continue
    print(f"doesn't exist on {name}")
    return ""

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
    init_keygroup(data, "testid", "test_data")
    keygroups.append(data)
    return getKeygroups()

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

# IP:host/getLocation: returns the satellite's location (?)
@app.route('/getLocation')
def getLocation():
    positions = read_file_from_node("manage", "positions")
    pos = json.loads(positions.data)
    return pos[name]

@app.route('/setLocation', methods=['POST'])
def setLocation():
    data = request.data.decode('UTF-8')
    positions = read_file_from_node("manage", "positions")
    pos = json.loads(positions.data)
    pos[name] = data
    add_data("manage", "positions", json.dumps(pos))
    return json.dumps(pos)

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
        # Keygroup doesn't exist yet
        init_pos = {f'{name}': {'x': 1, 'y': 2, 'z': 3}}
        init_keygroup("manage", "positions", json.dumps(init_pos))
    except Exception as e:
        # Keygroup already exists
        exist = True
    
    if(exist): 
        try:
            add_node_to_keygroup("manage")
        except Exception as e:
            # already inside
            pass

    app.run(debug=True, host=ip, port=port)