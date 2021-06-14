import grpc
import json
import math
from proto import client_pb2, client_pb2_grpc

STD_GRAVITATIONAL_PARAMETER_EARTH = 3.986004418e14

class FredClient:

    def __init__(self, name, target, client_crt, client_key, ca_crt):
        self.name = name

        creds = grpc.ssl_channel_credentials(
            certificate_chain=client_crt,
            private_key=client_key,
            root_certificates=ca_crt,
        )

        self.channel = grpc.secure_channel(target, credentials=creds)
        self.keygroups = ["manage"]
    
    # Initializes the keygroup
    def init_keygroup(self, kg):
        print(f"Initializing {kg} at {self.name}...")
        stub = client_pb2_grpc.ClientStub(self.channel)
        try:
            response = stub.CreateKeygroup(
                client_pb2.CreateKeygroupRequest(keygroup=kg, mutable=True)
            )
            self.keygroups.append(kg)
            print(f'giving {self.name} permission')
            self.give_user_permissions(self.name, kg, 4)
            print('gave permission')
            return True
        except:
            return False
    
    # Adds data to a keygroup
    def set_data(self, kg, key, value):
        print(f"Adding {key}:{value} to {kg}...")
        stub = client_pb2_grpc.ClientStub(self.channel)
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
                set_data(kg, key, json.dumps(cur_data))
    
    # Adds node to the keygroup
    def add_node_to_keygroup(self, kg, node, satellite):
        print(f"Adding {node} to {kg}...")
        try:
            stub = client_pb2_grpc.ClientStub(self.channel)
            response = stub.AddReplica(
                client_pb2.AddReplicaRequest(keygroup=kg, nodeId=node)
            )
            print(response)
            self.give_user_permissions(node, kg, 4)
            self.give_user_permissions(satellite, kg, 4)
            return True
        except Exception as e:
            print(e)
            return False
    
    def node_to_keygroup(self, kg, node):
        print(f"Adding {node} to {kg}...")
        try:
            stub = client_pb2_grpc.ClientStub(self.channel)
            response = stub.AddReplica(
                client_pb2.AddReplicaRequest(keygroup=kg, nodeId=node)
            )
            return str(response)
        except Exception as e:
            print(e)
            return str(e)
    
    # Removes node from the keygroup
    def remove_node_from_keygroup(self, kg, node):
        print(f"Removing {self.name} from {kg}...")
        stub = client_pb2_grpc.ClientStub(self.channel)
        response = stub.RemoveReplica(
            client_pb2.RemoveReplicaRequest(keygroup=kg, nodeId=node)
        )
        print(response)

    # Reads file
    def read_file_from_node(self, keygroup, file_id):
        try:
            print(f"Reading {file_id=} in {keygroup=} from {self.name=}...")
            stub = client_pb2_grpc.ClientStub(self.channel)
            response = stub.Read(
                client_pb2.ReadRequest(keygroup=keygroup, id=file_id)
            )
            print(response)
            return response
        except Exception as e:
            # if file does not exist an error is raised
            # return str(e)
            return ""

    # Reads file
    def read_file(self, file_id):
        for keygroup in self.keygroups:
            try:
                print(f"Reading {file_id=} in {keygroup=} from {self.name=}...")
                stub = client_pb2_grpc.ClientStub(self.channel)
                response = stub.Read(
                    client_pb2.ReadRequest(keygroup=keygroup, id=file_id)
                )
                return response
            except:
                # if file does not exist an error is raised
                continue
        print(f"doesn't exist on {self.name}")
        return ""


    def add_role(self, user, keygroup, role):
        try:
            stub = client_pb2_grpc.ClientStub(self.channel)
            response = stub.AddUser(
                client_pb2.UserRequest(
                    user=user, keygroup=keygroup, role=role)
            )
            return str(response)
        except Exception as e:
            return str(e)
    
    def get_keygroups(self):
        return self.keygroups
    
    def remove_keygroup(self, kg):
        self.keygroups.remove(kg)

    def calculate_orbit_period(self, semi_major_axis=0.0):
        """
        Calculates the period of a orbit for Earth.

        Parameters
        ----------
        semi_major_axis : float
            semi major axis of the orbit in meters

        Returns
        -------
        Period : int
            the period of the orbit in seconds (rounded to whole seconds)
        """

        tmp = math.pow(semi_major_axis, 3) / STD_GRAVITATIONAL_PARAMETER_EARTH
        return int(2.0 * math.pi * math.sqrt(tmp))