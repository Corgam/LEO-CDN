# LEO-CDN

Repository for the SoSe21 DSP Project: LEO-CDN

# Simulation-test

Starts two FReD nodes (`nodeB` and `nodeC`, corresponding to the nodes in the `FReD` tests) and a client (`tester`) that initializes a keygroup that is continuously passed between the two nodes.

## Setup

1. Generate certificates

- Generate certificates
  - `cd cert`
- Linux:
  - `sh gen-cert.sh nodeBx 172.26.2.1`
  - `sh gen-cert.sh nodeCx 172.26.3.1`
  - `sh gen-cert.sh keygroupPasser 172.26.4.1`

- Windows:
  - PowerShell:
    - `./gen-cert.sh nodeBx 172.26.2.1`
    - `./gen-cert.sh nodeCx 172.26.3.1`
    - `./gen-cert.sh keygroupPasser 172.26.4.1`
  - CMD:
    - `gen-cert.sh nodeBx 172.26.2.1`
    - `gen-cert.sh nodeCx 172.26.3.1`
    - `gen-cert.sh keygroupPasser 172.26.4.1`
2. Go back to the main folder (LEO-CDN)
3. Generate Python gRPC client: `make compile_grpc_python`
4. Start FReD nodes and NaSe: `make run_nodes`
5. Start tester: `make run_tester`

## Run

1. Make sure that the docker network and all its containers are deleted `make clean`
2. Start FReD nodes and NaSe: `make run_nodes`
3. Start tester: `make run_tester` (on Windows the Makefile should not contain `pwd`, replace it with global path)


## Generator.py

Generates certificates and a .yml file for each node. Adjusts the Makerfile and then runs docker-compose to start all storage and FReD nodes automatically.

- Use `py generator.py -node {number}`
