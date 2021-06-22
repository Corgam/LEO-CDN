import grpc
import json
from proto import client_pb2, client_pb2_grpc
import logging

class FredClient:
    def __init__(self, name, fred, target, client_crt, client_key, ca_crt):
        logging.basicConfig(filename='/logs/' + name + '.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
        self.logger = logging.getLogger(f'{name}_fred')
        self.fred = fred
        self.target = target
        self.name = name

        self.creds = grpc.ssl_channel_credentials(
            certificate_chain=client_crt,
            private_key=client_key,
            root_certificates=ca_crt,
        )

        self.channel = grpc.secure_channel(target, credentials=self.creds)
        self.keygroups = []
    
    def get_all_existing_replica_nodes(self):
        self.logger.info("Retrieving all replica nodes: ")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.GetAllReplica(
                client_pb2.GetAllReplicaRequest()
            )
        self.logger.info(status_response)

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
        self.logger.info(f"Initializing {keygroup} at {self.name}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.CreateKeygroup(
                client_pb2.CreateKeygroupRequest(keygroup=keygroup, mutable=mutable)
            )
        if status_response.status == 0:
            self.keygroups.append(keygroup)
            self.logger.info(f"Initializing succeeded...")
        else:
            self.logger.info(f"Failed initializing {keygroup} at {self.name}...")
        return status_response
    
    def add_replica_node_to_keygroup(self, keygroup):
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
        self.logger.info(f"Adding {self.name} to {keygroup}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.AddReplica(
                client_pb2.AddReplicaRequest(keygroup=keygroup, nodeId=self.fred)
            )

        if status_response.status == 0:
            self.keygroups.append(keygroup)
            self.logger.info(f"Adding succeeded...")
        else:
            self.logger.info(f"Failed adding {self.name} to {keygroup}...")

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
        self.logger.info(f"Removing {self.name} from {keygroup}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            status_response = stub.RemoveReplica(
                client_pb2.RemoveReplicaRequest(keygroup=keygroup, nodeId=node)
            )
        
        if status_response.status == 0:
            self.keygroups.remove(keygroup)
            self.logger.info(f"Removing succeeded...")
        else:
            self.logger.info(f"Failed removing {self.name} to {keygroup}...")

        return status_response

    # Adds data to a keygroup
    def set_data(self, kg, key, value):
        self.logger.info(f"Adding {key}:{value} to {kg}...")
        with grpc.secure_channel(self.target, credentials=self.creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            try:
                response = stub.Update(
                    client_pb2.UpdateRequest(keygroup=kg, id=key, data=value)
                )
                self.logger.info(response)
            except Exception as e:
                response = self.read_file_from_node(kg, key)
                if response:
                    cur_data = json.loads(response.data)
                    cur_data.append(value)
                    self.set_data(kg, key, json.dumps(cur_data))
    
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
                return response.data
            except:
                # if file does not exist an error is raised
                continue
        print(f"doesn't exist on {self.name}")
        return ""
    
    def get_keygroups(self):
        return self.keygroups
    
    def remove_keygroup(self, kg):
        self.keygroups.remove(kg)
