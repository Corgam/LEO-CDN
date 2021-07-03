# LEO-CDN

Repository for the SoSe21 DSP Project: LEO-CDN

Authors:

- Emil Balitzki
- Jonas Bernhard
- Abbas Fakhir
- Huy Viet Nguyen
- András Temesi
- Marek Wallich
- Hoang Mi Pham

## Requirements and setup

`pip install -r requirements.txt`

## Run Simulation

1. (Optional) Customize the config file.
2. Generate the workload `make generate_workload`.
3. Run `make setup` command.
4. Run `make satellites` command.
5. Run `make gsts` command.

## Generator

Generates certificates and a .yml file for each satellite. Creates a Makefile and then runs docker-compose to start all storage, FReD and HTTP-server nodes automatically. Furthermore, creates all necessary files to run the project.

## Ground Stations

Reads the list of groundstations from `temp/filename.txt` (specified in the Config file) and creates a thread for each of them. Groundstation will send n amount of requests (specified in the Config file) in an async fashion to the best satellite (received from the Coordinator).

## Satellite

https://github.com/Corgam/LEO-CDN/wiki/Satellite-API

## Coordinator

https://github.com/Corgam/LEO-CDN/wiki/Coordinator-API
