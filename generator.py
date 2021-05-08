import sys
import subprocess

# Validates command line argument
if len(sys.argv) != 3:
    print('generator.py -node <number>')
    exit()

if sys.argv[1] != "-node":
    print('generator.py -node <number>')
    exit()

if not sys.argv[2].isnumeric():
    print('generator.py -node <number>')
    exit()

if int(sys.argv[2]) < 1:
    print('Please use a number >0')
    exit()

# Number of nodes to generate
nodes = int(sys.argv[2])

# Generating certificates for every store and fred node
print('Generating certificates for', nodes, 'nodes...')

# Generate n certificates
# Run specific command based on OS
# Nodes will have IP starting from 127.26.7.1 (to not use the NS's IP)
# To prevent 'Anomalous backslash in string' warning: '\\' inside string
if sys.platform.startswith('win'):
      subprocess.call(".\\cert\\generate-n-certificates.sh '%s'" % str(nodes), shell=True)
elif sys.platform.startswith('linux'):
      subprocess.call("sh ./cert/generate-n-certificates.sh '%s'" % str(nodes), shell=True)

# Creating the yml files
print('Generating yml file for', nodes, 'nodes...')

for x in range(nodes):
    nodeIP = f"172.26.{x+7}.1"
    storeIP = f"172.26.{x+7}.2"
    nodeName = f"node{x}"
    storeName = f"store{x}"
    
    f = open(f"./docker/node{x}.yml", 'w')
    f.write(f"""version: "3.7"
services:
  {nodeName}:
    build: ../FReD
    depends_on:
      - {storeName}
    image: fred/fred:local
    container_name: {nodeName}
    entrypoint: "fred \\
    --remote-storage-host {storeIP}:1337 \\
    --peer-host {nodeIP}:5555 \\
    --nodeID nodeB \\
    --host {nodeIP}:9001 \\
    --cert /cert/node{x}.crt \\
    --key /cert/node{x}.key \\
    --ca-file /cert/ca.crt \\
    --adaptor remote \\
    --nase-host https://172.26.6.1:2379 \\
    --nase-cert /cert/node{x}.crt \\
    --nase-key /cert/node{x}.key \\
    --nase-ca /cert/ca.crt \\
    --handler dev \\
    --badgerdb-path ./db \\
    --remote-storage-cert /cert/node{x}.crt \\
    --remote-storage-key /cert/node{x}.key  \\
    --trigger-cert /cert/node{x}.crt \\
    --trigger-key /cert/node{x}.key\"
    environment:
      - LOG_LEVEL
    volumes:
      - ../cert/{nodeName}.crt:/cert/node{x}.crt
      - ../cert/{nodeName}.key:/cert/node{x}.key
      - ../cert/ca.crt:/cert/ca.crt
    ports:
      - {9000+x+3}:9001
    networks:
      fredwork:
        ipv4_address: {nodeIP}

  {storeName}:
    build:
      context: ../FReD
      dockerfile: storage.Dockerfile
    image: fred/store:local
    container_name: {storeName}
    entrypoint: "storageserver \\
    --log-level '${{LOG_LEVEL_STORE}}' \\
    --cert /cert/cert.crt \\
    --key /cert/key.key \\
    --ca-file /cert/ca.crt"
    volumes:
      - ../cert/{storeName}.crt:/cert/cert.crt
      - ../cert/{storeName}.key:/cert/key.key
      - ../cert/ca.crt:/cert/ca.crt
    networks:
      fredwork:
        ipv4_address: {storeIP}

networks:
  fredwork:
    external: true
""")


### Adjusting the Makefile ###
print('Generating Makerfile for', nodes, 'nodes...')

# Create a list of yml files
nodesString =""
for x in range(nodes):
    nodesString+=' -f docker/node{}.yml'.format(x)

# Write the Makefile
f = open('Makefile', 'w')
f.write(f"""
run_nodes:
	@docker network create fredwork --gateway 172.26.0.1 --subnet 172.26.0.0/16 || (exit 0)
	@docker-compose -f docker/etcd.yml {nodesString} build
	@docker-compose --env-file .env -f docker/etcd.yml {nodesString} up --force-recreate --abort-on-container-exit --renew-anon-volumes --remove-orphans

run_tester:
	@docker build -f ./Dockerfile -t keygroup-passer .
	@docker run -it \\
		--name keygroup-passer \\
		-v `pwd`/cert/keygroupPasser.crt:/cert/client.crt \\
		-v `pwd`/cert/keygroupPasser.key:/cert/client.key \\
		-v `pwd`/cert/ca.crt:/cert/ca.crt \\
		--network=fredwork \\
		--ip=172.26.4.1 \\
		keygroup-passer

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./proto/client.proto

clean:
	@docker network rm fredwork
	@docker-compose -f docker/etcd.yml {nodesString} down""")
f.close()

# Start a pre-cleaning
print('Start cleaning process..')
subprocess.call(['make', 'clean'])

# # Start running the nodes
print('Running', nodes, 'nodes...')
subprocess.call(['make','run_nodes'])
