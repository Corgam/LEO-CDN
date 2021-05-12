import grpc
from proto import client_pb2, client_pb2_grpc
import json

# Load node configurations
# TODO: Load only the needed one, not all
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

# Looks for a node in a nodes list with specified IP and port
def searchNode(ip, port):
    for node in node_configs.items():
        vals = node[1];
        # Check the ip and port
        if(node[1].get("host") == ip and node[1].get("port") == port):
            return nodes.index(node[0])
    return None

# Connects to specific satellite (Stores its index, IP and Port)
def start():
    # Search for the node in the list
    nodeID = searchNode(current_IP,current_Port)
    # If no found node return
    if(nodeID == None):
        return False
    # If node found return true
    global current_Node
    current_Node = nodes[nodeID]
    return True


# Disconnects with currently connected satellite.
def end(ip,port):
    print("")


# Tries to get a file with given ID from currently connected satellite.
def pull(keygroup, file_ID):
    # Try to request the file
    try:
        # Create a secure grpc channel and use it to create stub
        node_cfg = node_configs[current_Node]
        target = f"{node_cfg['host']}:{node_cfg['port']}"
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            # Try to receive the file
            response = stub.Read(
                client_pb2.ReadRequest(keygroup=keygroup, id=file_ID)
            )
            print(response)
            # TODO: Save file under given path
    except Exception as e:
        # If file does not exist an error is raised
        print("File with given file ID does not exist on currently connected satellite!")


# Adds a file to a keygroup of currently connected satellite.
def push(keygroup, file_ID, file):
    try:
        # Create a secure grpc channel and use it to create stub
        node_cfg = node_configs[current_Node]
        target = f"{node_cfg['host']}:{node_cfg['port']}"
        with grpc.secure_channel(target, credentials=creds) as channel:
            stub = client_pb2_grpc.ClientStub(channel)
            # Try to receive the file
            response = stub.Update(
                client_pb2.UpdateRequest(keygroup=keygroup, id=file_ID, data=file)
            )
            print(response)
    except Exception as e:
        # If file does not exist an error is raised
        print("Error while uploading a file with given file ID to currently connected satellite!")

# Global variables - currently connected satellite info
current_IP = None
current_Port = None
current_Node = None

# Print welcome msg
print("\n")
print("Welcome pionier! You are accessing the STARDUST,\nalso known as Satellite Transmitting and Receiving Data Utility Simplification Tool.")
print("Type 'help' for list of all available commands and info.")
print("\n")
running = True
# Constantly check for user input
while(running):
    command = input()
    # Prints all commands and their uses
    if(command == "help"):
        print("\n")
        print("Stardust allows for easy access to data stored in selected satellite. After connecting to a satellite,\none can request a specified data or upload a new file.")
        print("List of available commands and their usage:")
        print("     'start <IP> <Port>' - Starts connection to a specified satellite.")
        print("     'pull <fileID> <filePath>' - Requests from the satellite a file with given file ID and saves it at given location.")
        print("     'push <fileID> <filePath> ' - Sends a file from given path to the satellite and saves it under given file ID.")
        print("     'end' - Ends connection with currently connected satellite.")
        print("     'exit' - Terminate SIP.")
        print("\n")
    # Exit the while loop
    elif(command == "exit"):
        running = False
    elif(command.startswith("start ")):
        # Split the command 
        args = command.rsplit(' ', 2)
        # Check if usage was correct
        if(len(args) != 3):
            print("Invalid usage of command. Type 'help' to see the usage.")
            continue
        current_IP = args[1]
        current_Port = args[2]
        # Try to connect to the node
        if(start()):
            # Connected to specified node
            print(f"\nSuccessfully connected to the node with ID {current_IP} on Port {current_Port}.")
        else:
            # If no node with given ip and port is found reset variables
            print(f"\nCannot connect to node with ID {current_IP} on Port {current_Port}.")
            current_Port = None
            current_IP = None
            current_Node = None
    # Disconnect with currently connected satellite
    elif(command.startswith("end")):
        print(f"\nDisconnecting with the node with ID {current_IP} on Port {current_Port}.")
        current_Port = None
        current_IP = None
        current_Node = None
    # Trying to receive a file from the satellite
    elif(command.startswith("pull ")):
        # Check if we have connected with some satellite
        if(current_Node == None):
            print("Before you pull data, you need to connect to a satellite. Type 'help' for more info.")
            continue
        # Split the command 
        args = command.rsplit(' ', 2)
        # Check if usage was correct
        if(len(args) != 3):
            print("Invalid usage of command. Type 'help' to see the usage.")
            continue
        fileID = args[1]
        savePath = args[2]
        keygroup = "northernfiles" # TODO - Use non static keygroup?
        # Request the file
        pull(keygroup,fileID)
    # Sending a file to the satellite
    elif(command.startswith("push ")):
        # Check if we have connected with some satellite
        if(current_Node == None):
            print("Before you push data, you need to connect to a satellite. Type 'help' for more info.")
            continue
        # Split the command 
        args = command.rsplit(' ', 2)
        # Check if usage was correct
        if(len(args) != 3):
            print("Invalid usage of command. Type 'help' to see the usage.")
            continue
        fileID = args[1]
        locationPath = args[2]
        file = "SPAAACE!!" #TODO load file from given location
        keygroup = "northernfiles" # TODO - Use non static keygroup?
        # Send the file
        push(keygroup,fileID,file)
    # If command is unknown, print a help msg
    else:
        print("\n")
        print("Command unknown. Please use 'help' for a list of all available commands.")
        print("\n")