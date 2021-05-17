# LEO-CDN

Repository for the SoSe21 DSP Project: LEO-CDN

## Setup

`pip install -r requirements.txt`
## Requirements

- Docker
- Python

## Run Simulation

1. Run `make generate_nodes n=<int>` (e.g. `make generate_nodes n=3` for generating 3 nodes)
2. Run `make run_nodes`
3. Run `make run_tester`

Steps 1. and 2. can be run together with `make generate_and_run_nodes n=<int>`

## Generator.py

Generates certificates and a .yml file for each node. Creates a Makerfile and then runs docker-compose to start all storage and FReD nodes automatically.

- Usage `make generate_nodes n=<int>` whereas `n` indicates the number of nodes

## keygroup_passer.py

Manages the communication between nodes. The first node initializes a keygroup and adds data into the keygroup. Afterwards the keygroup gets passed between all nodes.

- Usage `make run_tester`
