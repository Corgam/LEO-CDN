# LEO-CDN

Repository for the SoSe21 DSP Project: LEO-CDN

## Setup

`pip install -r requirements.txt`

## Requirements

- Docker
- Python
- Jinja2

## Run Simulation

1. Run `make generate_nodes n=<int>` (e.g. `make generate_nodes n=3` for generating 3 nodes)
2. Run `make run_nodes`
3. Run `make run_client` to see basic satellite communication
4. Run `make run_tester`
5. Run `make stardust` to pull/push satellite's data

Steps 1. and 2. can be run together with `make generate_and_run_nodes n=<int>`

## Generator.py

Generates certificates and a .yml file for each node. Creates a Makerfile and then runs docker-compose to start all storage and FReD nodes automatically.

- Usage `make generate_nodes n=<int>` whereas `n` indicates the number of nodes

## keygroup_passer.py

Manages the communication between nodes. The first node initializes a keygroup and adds data into the keygroup. Afterwards the keygroup gets passed between all nodes.

- Usage `make run_tester`

## Stardust v1.0

Satellite Transmitting and Receiving Data Utility Simplification Tool.

First version of the GST-Satellite interface. Can connect to a chosen satellite and pull/push data from/to it.

- Usage `make stardust`

Note: `make run_tester` needs to be run first to create a keygroup.

## satellite_server.py

HTTP Server for a satellite, provides following end-points:

| Method  | Route | Body | Description |
| ------------- | ------------- | ------------- | ------------- |
| GET  | IP:5000/getKeygroups  | - |Retrieves all keygroups of a fred node |
| POST  | IP:5000/initializeKeygroup  | keygroup (string) | Initializes a keygroup |
| POST  | IP:5000/addKeygroup  | keygroup (string) | Adds the fred node to a keygroup |
| POST  | IP:5000/removeKeygroup  | keygroup (string) | Removes the fred node from a keygroup |
| GET  | IP:5000/getValue/&lt;keygroup>/&lt;key>  | - | Retrieves data from a specific keygroup with a given key |
| GET  | IP:5000/getValue/&lt;key>  | - | Goes through all keygroups of the fred node and tries to retrieve data with a given key |
| GET  | IP:5000/getLocation  | - | Returns a json with the following format: {x: &lt;number>, y: &lt;number>, z: &lt;number>} |
| POST  | IP:5000/setLocation  | {x: &lt;number>, y: &lt;number>, z: &lt;number>} | Sets the fred node's position by modifying the node coordinate data in the manage keygroup |
| GET  | IP:5000/positions  | - | Returns the position from all nodes (keygroup: manage, key: positions) |