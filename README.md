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
2. Run `sudo apt-get upgrade`.
3. Install Docker 20.10.8 and docker-compose (Follow https://docs.docker.com/engine/install/ubuntu/ and `sudo apt-get install docker-compose`).
4. Install Python 3.8 (`sudo apt-get install python3.8`, `sudo apt-get install python3-pip` and `sudo apt install python-is-python3`).
5. Install GNU Make 4.2.1 (`sudo apt-get install build-essential`).
6. Install Git and clone this repository together with its submodules (`sudo apt-get install git` and `git clone https://github.com/Corgam/LEO-CDN`).
The `FReD` submodule should be cloned from `jb/add-disable-rbac-option` branch.
8. Run `pip3 install -r requirements.txt`.

## Run Simulation

1. (Optional) Customize the config file.
2. Generate the workload `sudo make workload`.
3. Run `sudo make setup` command.
4. Run `sudo make satellites` command.
5. Run `sudo make gsts` command.

## Generator

Generates certificates and a .yml file for each satellite. Creates a Makefile and then runs docker-compose to start all storage, FReD and HTTP-server nodes automatically. Furthermore, creates all necessary files to run the project.

## Ground Stations

Reads the list of groundstations from `temp/filename.txt` (specified in the Config file) and creates a thread for each of them. Groundstation will send n amount of requests (specified in the Config file) in an async fashion to the best satellite (received from the Coordinator).

## Satellite

https://github.com/Corgam/LEO-CDN/wiki/Satellite-API

## Coordinator

https://github.com/Corgam/LEO-CDN/wiki/Coordinator-API
