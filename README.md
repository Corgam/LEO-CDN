# LEO-CDN

Repository for the SoSe21 DSP Project: LEO-CDN

# Requirements

- Docker
- Python

# Run Simulation

1. Run `py .\generator.py -node {number}`
2. Run `make run_tester`

## Generator.py

Generates certificates and a .yml file for each node. Creates a Makerfile and then runs docker-compose to start all storage and FReD nodes automatically.

- Usage `py generator.py -node {number}` whereas number indicates the number of nodes

## keygroup_passer.py

Manages the communication between nodes. The first node initializes a keygroup and adds data into the keygroup. Afterwards the keygroup gets passed between all nodes.

- Usage `make run_tester'
