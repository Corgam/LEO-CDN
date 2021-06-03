# Loading node configurations
import json

from satellite.proto import client_pb2, client_pb2_grpc
import grpc

# Loading certificates
with open("./common/cert/client.crt", "rb") as f:
    client_crt = f.read()

with open("./common/cert/client.key", "rb") as f:
    client_key = f.read()

with open("./common/cert/ca.crt", "rb") as f:
    ca_crt = f.read()

creds = grpc.ssl_channel_credentials(
    certificate_chain=client_crt,
    private_key=client_key,
    root_certificates=ca_crt,
)

# TODO connect this pls with the server and change in satellite.py the calls accordingly

def create_keygroup(target_node, keygroup, mutable=True, expiry=0):
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
    print(f"Initializing {keygroup=} at {target_node=}...")
    with open(f"/temp/{target_node}.json") as f:
        node_configs = json.load(f)

    node_cfg = node_configs[target_node]
    target = f"{node_cfg['node']}:{node_cfg['nport']}"
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        status_response = stub.CreateKeygroup(
            client_pb2.CreateKeygroupRequest(keygroup=keygroup, mutable=mutable, expiry=expiry)
        )
    return status_response


def add_replica_node_to_keygroup(target_node, keygroup):
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
    print(f"Adding {target_node=} to {keygroup=}...")
    with open(f"/temp/{target_node}.json") as f:
        node_configs = json.load(f)

    node_cfg = node_configs[target_node]
    target = f"{node_cfg['node']}:{node_cfg['nport']}"
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        status_response = stub.AddReplica(
            client_pb2.AddReplicaRequest(keygroup=keygroup, nodeId=target_node)
        )
    return status_response


def remove_replica_node_from_keygroup(target_node, keygroup):
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
    print(f"Removing {target_node=} from {keygroup=}...")
    with open(f"/temp/{target_node}.json") as f:
        node_configs = json.load(f)

    node_cfg = node_configs[target_node]
    target = f"{node_cfg['node']}:{node_cfg['nport']}"
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        status_response = stub.RemoveReplica(
            client_pb2.RemoveReplicaRequest(keygroup=keygroup, nodeId=target_node)
        )
    return status_response
