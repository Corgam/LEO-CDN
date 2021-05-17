import grpc
from proto import client_pb2, client_pb2_grpc
import time
import json

# Loading node configurations
with open('./nodes.json') as f:
  node_configs = json.load(f)

nodes = [key for key in node_configs.keys()]


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

# Test keygroup & file
KEYGROUP = "northernfiles"
FILE_ID = "somefile"

# Initializes the keygroup
def init_keygroup(target_node, keygroup=KEYGROUP):
    print(f"Initializing {keygroup=} at {target_node=}...")
    node_cfg = node_configs[target_node]
    print(node_cfg)
    target = f"{node_cfg['host']}:{node_cfg['port']}"
    print(target)
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        response = stub.CreateKeygroup(
            client_pb2.CreateKeygroupRequest(keygroup=KEYGROUP, mutable=True)
        )
        print(response)
        response = stub.Update(
            client_pb2.UpdateRequest(keygroup=KEYGROUP, id=FILE_ID, data=":-)")
        )
        print(response)
        # Add Stardust to write role
        response = stub.AddUser(
            client_pb2.UserRequest(user="stardust",keygroup=KEYGROUP,role="WriteKeygroup")
        )
        print(response)
        # Add Stardust to read role
        response = stub.AddUser(
            client_pb2.UserRequest(user="stardust",keygroup=KEYGROUP,role="ReadKeygroup")
        )
        print(response)

# Adds node to the keygroup
def add_node_to_keygroup(target_node, keygroup=KEYGROUP):
    print(f"Adding {target_node=} to {keygroup=}...")
    node_cfg = node_configs[target_node]
    print(node_cfg)
    target = f"{node_cfg['host']}:{node_cfg['port']}"
    print(target)
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        response = stub.AddReplica(
            client_pb2.AddReplicaRequest(keygroup=KEYGROUP, nodeId=target_node)
        )
        print(response)

# Removes node from the keygroup
def remove_node_from_keygroup(target_node, keygroup=KEYGROUP):
    print(f"Removing {target_node=} from {keygroup=}...")
    node_cfg = node_configs[target_node]
    target = f"{node_cfg['host']}:{node_cfg['port']}"
    with grpc.secure_channel(target, credentials=creds) as channel:
        stub = client_pb2_grpc.ClientStub(channel)
        response = stub.RemoveReplica(
            client_pb2.RemoveReplicaRequest(keygroup=KEYGROUP, nodeId=target_node)
        )
        print(response)

# Reads file
def read_file_from_nodes(keygroup=KEYGROUP, file_id=FILE_ID):
    for target_node in nodes:
        try:
            print(f"Reading {file_id=} in {keygroup=} from {target_node=}...")
            node_cfg = node_configs[target_node]
            target = f"{node_cfg['host']}:{node_cfg['port']}"
            with grpc.secure_channel(target, credentials=creds) as channel:
                stub = client_pb2_grpc.ClientStub(channel)
                response = stub.Read(
                    client_pb2.ReadRequest(keygroup=keygroup, id=file_id)
                )
                print(response)
                print(f"File exists on node {target_node}!")
        except Exception as e:
            # if file does not exist an error is raised
            print(f"File does NOT exist on node {target_node}!")

current_node_ind = 0
init_keygroup(nodes[current_node_ind])

period = 10
duration_per_node = period // len(nodes)

current_time = 0
while True:
    print("================")
    current_time += 1

    target_node_ind = current_node_ind

    if(current_time >= duration_per_node):
        target_node_ind = (current_node_ind + 1) % len(nodes)
    
    current_node = nodes[current_node_ind]
    target_node = nodes[target_node_ind]

    print(f"{current_time=}, {current_node=}, {target_node=}")

    if target_node != current_node:
        print(
            f"Switching node that hosts keygroup from {current_node} to {target_node}..."
        )
        add_node_to_keygroup(target_node)
        remove_node_from_keygroup(current_node)

    current_node_ind = target_node_ind

    read_file_from_nodes()

    print("================")
    print("\n")
    time.sleep(5)