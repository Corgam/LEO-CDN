# LEO-CDN

Repository for the SoSe21 DSP Project: LEO-CDN

## Requirements and setup

`pip install -r requirements.txt`

## Run Simulation

1. (Optional) Customize the config file.
2. Run `make setup` command.
3. Run `make coordinator` command.
4. Run `make stardust` command.

## Generator.py

Generates certificates and a .yml file for each satellite. Creates a Makefile and then runs docker-compose to start all storage, FReD and HTTP-server nodes automatically.

- Usage `make generate`.

## Coordinator

Runs the simulation inside and keeps track of the positions of all satellites and groundstations at any given time.
Moreover, listens on port 9001 for any groundstation related HTTP Requests and responds with the best satellite that the sender can currently connect to.

IP: 172.26.4.1
Port: 9001

## Stardust (Ground Stations)

Satellite Transmitting and Receiving Data Utility Simplification Tool.

Reads HTTP Requests from requests.txt file and sends them to the best satellite. The best satellite is chosen with the help of the coordinator.

## satellite_server.py

HTTP Server for a satellite, provides following end-points:

| Method | Route                                   | Body                                             | Description                                                                                |
| ------ | --------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| GET    | IP:5000/getKeygroups                    | -                                                | Retrieves all keygroups of a fred node                                                     |
| POST   | IP:5000/initializeKeygroup              | keygroup (string)                                | Initializes a keygroup                                                                     |
| POST   | IP:5000/addKeygroup                     | keygroup (string)                                | Adds the fred node to a keygroup                                                           |
| POST   | IP:5000/removeKeygroup                  | keygroup (string)                                | Removes the fred node from a keygroup                                                      |
| GET    | IP:5000/getValue/&lt;keygroup>/&lt;key> | -                                                | Retrieves data from a specific keygroup with a given key                                   |
| GET    | IP:5000/getValue/&lt;key>               | -                                                | Goes through all keygroups of the fred node and tries to retrieve data with a given key    |
| GET    | IP:5000/getLocation                     | -                                                | Returns a json with the following format: {x: &lt;number>, y: &lt;number>, z: &lt;number>} |
| POST   | IP:5000/setLocation                     | {x: &lt;number>, y: &lt;number>, z: &lt;number>} | Sets the fred node's position by modifying the node coordinate data in the manage keygroup |
| GET    | IP:5000/positions                       | -                                                | Returns the position from all nodes (keygroup: manage, key: positions)                     |
