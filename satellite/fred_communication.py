# Loading node configurations
import json
import toml

from proto import client_pb2, client_pb2_grpc
import grpc

class FredCommunication:

    def __init__(self, name, target, client_crt, client_key, ca_crt):
        self.name = name

        self.creds = grpc.ssl_channel_credentials(
            certificate_chain=client_crt,
            private_key=client_key,
            root_certificates=ca_crt,
        )

        self.target = target

    # TODO: connect this pls with the server and change in satellite.py the calls accordingly
    def get_all_existing_replica_nodes(self):
        print("Retrieving all replica nodes: ")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.GetAllReplica(
                client_pb2.GetAllReplicaRequest()
            )
        print(status_response)


    def create_keygroup(self, keygroup, mutable=True, expiry=0):
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
        print(f"Initializing {keygroup=} at {self.target=}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.CreateKeygroup(
                client_pb2.CreateKeygroupRequest(keygroup=keygroup, mutable=mutable, expiry=expiry)
            )
        return status_response


    def add_replica_node_to_keygroup(self, node, keygroup):
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
        print(f"Adding {self.target=} to {keygroup=}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.AddReplica(
                client_pb2.AddReplicaRequest(keygroup=keygroup, nodeId=node)
            )
        return status_response


    def remove_replica_node_from_keygroup(self, node, keygroup):
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
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.RemoveReplica(
                client_pb2.RemoveReplicaRequest(keygroup=keygroup, nodeId=node)
            )
        return status_response


    # Adds data to a keygroup
    def set_data(self, kg, key, value):
        print(f"Adding {key}:{value} to {kg}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            try:
                response = stub.Update(
                    client_pb2.UpdateRequest(keygroup=kg, id=key, data=value)
                )
                print(response)
            except Exception as e:
                response = self.read_file_from_node(kg, key)
                if response:
                    cur_data = json.loads(response.data)
                    cur_data.append(value)
                    self.set_data(kg, key, json.dumps(cur_data))

    # Reads file
    def read_file_from_node(self, keygroup, file_id):
        try:
            print(f"Reading {file_id=} in {keygroup=}...")
            with grpc.secure_channel(self.target, credentials=self.creds) as channel:
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

    def append_data(self, keygroup, key, entry):
        response = self.read_file_from_node(keygroup, key)
        if not response:
            cur_data = []
            cur_data.append(entry)
            self.set_data(keygroup, key, json.dumps(cur_data))
        else:
            cur_data = json.loads(response.data)
            cur_data.append(entry)
            self.set_data(keygroup, key, json.dumps(cur_data))
        return json.dumps(cur_data)
        # return response

    def join_managing_keygroups(self, fred, ip, port):
        try_joining = False
        try:
            self.create_keygroup("manage")
            self.set_data("manage", "addresses", json.dumps(["http://" + ip + ":" + str(port) + "/"]))
        except:
            print('"manage" keygroup already exists. Trying to join...')
            self.add_replica_node_to_keygroup(fred, "manage")
            self.append_data("manage", "addresses", "http://" + ip + ":" + str(port) + "/")
            
