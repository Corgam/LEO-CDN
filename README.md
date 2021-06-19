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

Generates certificates and a .yml file for each satellite. Creates a Makefile and then runs docker-compose to start all storage, FReD and HTTP-server nodes automatically. Furthermore, creates all necessary files to run the project.

- Usage: `make generate` 

## Stardust (Ground Stations)

Satellite Transmitting and Receiving Data Utility Simplification Tool.

Reads the list of groundstations from `temp/filename.txt` (specified in the Config file) and creates a thread for each of them. Groundstation will send n amount of requests ( specified in the Config file) to the best satellite (received from the Coordinator).

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


## Coordinator

Please take a look [here](https://github.com/Corgam/LEO-CDN/wiki/Coordinator-API).
