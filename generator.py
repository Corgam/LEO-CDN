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

# amount of nodes for our simulation
nodes = int(sys.argv[2])

# Generating certificates for every store and fred node
print('Generating certificates for', nodes, 'nodes...')

for x in range(nodes):
    subprocess.call(["bash.exe",'./cert/gen-cert-default.sh', './cert/store{}'.format(x+1),'172.26.{}.2'.format(x+3  if x+2 >= 6  else x+2)])
    subprocess.call(['sh','./cert/gen-cert.sh', './cert/node{}x'.format(x+1),'172.26.{}.1'.format(x+3  if x+2 >= 6  else x+2)])

# Creating the yml files
print('Generating yml file for', nodes, 'nodes...')

for x in range(nodes):
    nodeIP = '172.26.{}.1'.format(x+3 if x+2 >= 6 else x+2)
    storeIP = '172.26.{}.2'.format(x+3 if x+2 >= 6 else x+2)
    nodeName = 'node{}'.format(x+1)
    storeName = 'store{}'.format(x+1)
    
    f = open('./docker/node{}.yml'.format(x+1), 'w')
    f.write('''version: "3.7"

services:
  {}:
    build: ../FReD
    depends_on:
      - {}
    image: fred/fred:local
    container_name: {}
    entrypoint: "fred \\
    --remote-storage-host {}:1337 \\
    --peer-host {}:5555 \\
    --nodeID nodeB \\
    --host {}:9001 \\
    --cert /cert/node.crt \\
    --key /cert/node.key \\
    --ca-file /cert/ca.crt \\
    --adaptor remote \\
    --nase-host https://172.26.6.1:2379 \\
    --nase-cert /cert/node.crt \\
    --nase-key /cert/node.key \\
    --nase-ca /cert/ca.crt \\
    --handler dev \\
    --badgerdb-path ./db \\
    --remote-storage-cert /cert/node.crt \\
    --remote-storage-key /cert/node.key  \\
    --trigger-cert /cert/node.crt \\
    --trigger-key /cert/node.key"
    environment:
      - LOG_LEVEL
    volumes:
      - ../cert/{}x.crt:/cert/node.crt
      - ../cert/{}x.key:/cert/node.key
      - ../cert/ca.crt:/cert/ca.crt
    ports:
      - 900{}:9001
    networks:
      fredwork:
        ipv4_address: {}

  {}:
    build:
      context: ../FReD
      dockerfile: storage.Dockerfile
    image: fred/store:local
    container_name: {}
    entrypoint: "storageserver \\
    --log-level '${{LOG_LEVEL_STORE}}' \\
    --cert /cert/cert.crt \\
    --key /cert/key.key \\
    --ca-file /cert/ca.crt"
    volumes:
      - ../cert/{}.crt:/cert/cert.crt
      - ../cert/{}.key:/cert/key.key
      - ../cert/ca.crt:/cert/ca.crt
    networks:
      fredwork:
        ipv4_address: {}

networks:
  fredwork:
    external: true
'''.format(nodeName, 
    storeName, nodeName, 
    storeIP, nodeIP, 
    nodeIP, nodeName, 
    nodeName, x+3, 
    nodeIP, storeName, 
    storeName, storeName, 
    storeName, storeIP))
    f.close()

# Adjusting the Makerfile
print('Generating Makerfile for', nodes, 'nodes...')

nodesString =""
for x in range(nodes):
    nodesString+=' -f docker/node{}.yml'.format(x+1)

f = open('Makefile', 'w')
f.write('''run_nodes:
#Check if the docker network "fredwork" is already created, if not create one.
	@docker network create fredwork --gateway 172.26.0.1 --subnet 172.26.0.0/16 || (exit 0)
	@docker-compose -f docker/etcd.yml''')
f.write(nodesString)
f.write(' build\n')
f.write('	@docker-compose --env-file .env -f docker/etcd.yml')
f.write(nodesString)
f.write(' up --force-recreate --abort-on-container-exit --renew-anon-volumes --remove-orphans\n\n')
f.write('''run_tester:
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
	@docker-compose -f docker/etcd.yml''')
f.write(nodesString)
f.write(' down')
f.close()

# Start a pre-cleaning
print('Start cleaning process..')
subprocess.call(['make', 'clean'])

# Start running the nodes
print('Running', nodes, 'nodes...')
subprocess.call(['make','run_nodes'])
