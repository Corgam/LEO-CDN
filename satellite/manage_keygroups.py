# Loading node configurations
import json
import toml

from proto import client_pb2, client_pb2_grpc
import grpc

# Loading certificates
with open("/common/cert/client.crt", "rb") as f:
    client_crt = f.read()

with open("/common/cert/client.key", "rb") as f:
    client_key = f.read()

with open("/common/cert/ca.crt", "rb") as f:
    ca_crt = f.read()

creds = grpc.ssl_channel_credentials(
    certificate_chain=client_crt,
    private_key=client_key,
    root_certificates=ca_crt,
)

# Load the config
with open("/config.toml") as f:
    config = toml.load(f)


# Loading node configurations
with open("/info/node.json") as f:
    node_configs = json.load(f)

name = list(node_configs.keys())[0]
ip = node_configs[name]['server']
port = node_configs[name]['sport']
fred = node_configs[name]['fred']
target = f"{node_configs[name]['node']}:{node_configs[name]['nport']}"


# TODO: connect this pls with the server and change in satellite.py the calls accordingly
def get_all_existing_replica_nodes():
    print("Retrieving all replica nodes: ")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        status_response = stub.GetAllReplica(
            client_pb2.GetAllReplicaRequest()
        )
    print(status_response)


def create_keygroup(keygroup, mutable=True, expiry=0):
    """
    Parameters
    ----------
    target_node: str
        Has to be in the format "node<nodeId>". NodeId starts with 0.
        This is for indexing the correct host and port in the nodes.json file.
    keygroup: str
        Name or ID of the keygroup.
    mutable: bool
        Tells whether the keygroup is mutable or not.
    expiry: int
        Time until data in keygroup expires. If this value is 0 the expiry of data is deactivated.
        0 is also the default value.
    Returns
    -------
    status_response: StatusResponse
        The parsed response of creating a keygroup.
        It consists of an status and a message if the status is 1.
        1 means error and 0 means OK.
    """
    # print(f"Initializing {keygroup=} at {target_node=}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        status_response = stub.CreateKeygroup(
            client_pb2.CreateKeygroupRequest(keygroup=keygroup, mutable=mutable, expiry=expiry)
        )
    return status_response


def add_replica_node_to_keygroup(node, keygroup):
    """
    Adds a replica node to a keygroup.
    Parameters
    ----------
    target_node: str
        Has to be in the format "node<nodeId>". NodeId starts with 0.
        This is for indexing the correct host and port in the nodes.json file.
    keygroup: str
        Name or ID of the keygroup.
    Returns
    -------
    status_response: StatusResponse
        The parsed response of adding a replica node to a keygroup.
        It consists of an status and a message if the status is 1.
        1 means error and 0 means OK.
    """
    try:
        return create_keygroup(keygroup)
    except Exception as e:
        # print(f"Adding {target_node=} to {keygroup=}...")
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.AddReplica(
                client_pb2.AddReplicaRequest(keygroup=keygroup, nodeId=node)
            )
        return status_response


def remove_replica_node_from_keygroup(node, keygroup):
    """
    Removes a replica node from a keygroup.
    Parameters
    ----------
    target_node: str
        Has to be in the format "node<nodeId>". NodeId starts with 0.
        This is for indexing the correct host and port in the nodes.json file.
    keygroup: str
        Name or ID of the keygroup.
    Returns
    -------
    status_response: StatusResponse
        The parsed response of removing a replica node to a keygroup.
        It consists of an status and a message if the status is 1.
        1 means error and 0 means OK.
    """
    # print(f"Removing {target_node=} from {keygroup=}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        status_response = stub.RemoveReplica(
            client_pb2.RemoveReplicaRequest(keygroup=keygroup, nodeId=node)
        )
    return status_response


# Adds data to a keygroup
def set_data(kg, key, value):
    print(f"Adding {key}:{value} to {kg}...")
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        try:
            response = stub.Update(
                client_pb2.UpdateRequest(keygroup=kg, id=key, data=value)
            )
            print(response)
        except Exception as e:
            response = read_file_from_node(kg, key)
            if response:
                cur_data = json.loads(response.data)
                cur_data.append(value)
                set_data(kg, key, json.dumps(cur_data))

# Reads file
def read_file_from_node(keygroup, file_id):
    try:
        print(f"Reading {file_id=} in {keygroup=}...")
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            response = stub.Read(
                client_pb2.ReadRequest(keygroup=keygroup, id=file_id)
            )
            print(response)
            return response
    except Exception as e:
        # if file does not exist an error is raised
        # return str(e)
        return ""

def append_data(keygroup, key, entry):
    response = read_file_from_node(keygroup, key)
    if not response:
        cur_data = []
        cur_data.append(entry)
        set_data(keygroup, key, json.dumps(cur_data))
    else:
        cur_data = json.loads(response.data)
        cur_data.append(entry)
        set_data(keygroup, key, json.dumps(cur_data))
    return json.dumps(cur_data)
    # return response

def join_managing_keygroups():
    try_joining = False

    success = create_keygroup("manage")
    if not success == 0:
        print('"manage" keygroup already exists. Trying to join...')
        add_replica_node_to_keygroup(fred, "manage")
        append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
    else:
        set_data("manage", "addresses", json.dumps(["http://" + ip + ":" + str(port) + "/"]))
