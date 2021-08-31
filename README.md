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

1. Setup Ubuntu 20.04.3
2. Install Docker 20.10.8 and docker-compose (Follow https://docs.docker.com/engine/install/ubuntu/ and `sudo apt-get install docker-compose`).
3. Install Python 3.8 (`sudo apt-get install python3.8`, `sudo apt-get install python3-pip`).
4. Install GNU Make 4.2.1 (`sudo apt-get install build-essential`).
5. Install Git and clone this repository together with its submodules (`sudo apt-get install git`, `git clone https://github.com/Corgam/LEO-CDN` and `git submodule init`).
The `FReD` submodule should be cloned from `jb/add-disable-rbac-option` branch (`cd FReD/` and `git reset --hard origin/jb/add-disable-rbac-option`).
6. Run `pip3 install -r requirements.txt`.

## Run Simulation

1. (Optional) Customize the config file.
2. Generate the workload `sudo make workload`.
3. Run `sudo make setup` command.
4. Run `sudo make satellites` command.
5. Run `sudo make gsts` command.

If the first two make commands do not work, try:
1. `python3 generate_workload.py`.
2. `python3 generator.py`.
3. `sudo make coordinator`.
4. `sudo make satellites`.
5. `sudo make gsts`.

The coordinator, satellites and gsts need to be executed in different terminals.

## Generator

Generates certificates and a .yml file for each satellite. Creates a Makefile and then runs docker-compose to start all storage, FReD and HTTP-server nodes automatically. Furthermore, creates all necessary files to run the project.

## Ground Stations

Reads the list of groundstations from `temp/filename.txt` (specified in the Config file) and creates a thread for each of them. Groundstation will send n amount of requests (specified in the Config file) in an async fashion to the best satellite (received from the Coordinator).

## Satellite

https://github.com/Corgam/LEO-CDN/wiki/Satellite-API

## Coordinator

https://github.com/Corgam/LEO-CDN/wiki/Coordinator-API
